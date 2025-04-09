# chatbot/utils/dashboard_service.py
import json
from datetime import datetime, timedelta

class DashboardService:
    """
    Service for generating project dashboards
    """
    def __init__(self, sheets_client=None):
        from .google_sheets import GoogleSheetsClient
        self.sheets_client = sheets_client or GoogleSheetsClient()
    
    def generate_project_dashboard(self, project_name=None, sheet_name=None):
        """
        Generate dashboard data for a specific project or all projects
        
        Args:
            project_name (str, optional): Specific project to generate dashboard for
            sheet_name (str, optional): Specific sheet to get data from
            
        Returns:
            dict: Dashboard data
        """
        try:
            if project_name:
                # Get specific project data
                project = self.sheets_client.get_project_by_name(project_name, sheet_name)
                if not project:
                    return {'error': f"Project '{project_name}' not found"}
                
                members = self.sheets_client.get_project_members(project_name=project_name, sheet_name=sheet_name)
                return self._generate_single_project_dashboard(project, members)
            else:
                # Generate overview dashboard
                projects = self.sheets_client.get_all_projects(sheet_name) if sheet_name else self.sheets_client.get_all_projects_from_all_sheets()
                return self._generate_overview_dashboard(projects)
        except Exception as e:
            print(f"Error generating dashboard: {e}")
            return {
                'error': str(e),
                'projects_count': 0,
                'status_distribution': "{}",
                'budget': {
                    'total': 0,
                    'expenses': 0,
                    'remaining': 0,
                    'utilization_percentage': 0,
                    'over_budget_count': 0
                },
                'forecast': "[]",
                'recent_projects': []
            }
    
    def _generate_single_project_dashboard(self, project, members):
        """Generate dashboard for a single project"""
        try:
            # Calculate timeline progress
            timeline_data = self._calculate_timeline_progress(project)
            
            # Calculate budget utilization
            budget_data = self._calculate_budget_utilization(project)
            
            # Analyze team composition
            team_data = self._analyze_team_composition(members)
            
            return {
                'project': project,
                'timeline': timeline_data,
                'budget': budget_data,
                'team': team_data,
                'overview': {
                    'status': project.get('status', 'unknown'),
                    'members_count': len(members),
                    'budget_status': 'over_budget' if float(project.get('expenses', 0)) > float(project.get('budget', 0)) else 'under_budget',
                    'progress_percentage': timeline_data.get('percentage', 0)
                }
            }
        except Exception as e:
            print(f"Error generating single project dashboard: {e}")
            return {
                'error': str(e),
                'project': project,
                'timeline': {},
                'budget': {},
                'team': {'members': members},
                'overview': {}
            }
    
    def _generate_overview_dashboard(self, projects):
        """Generate overview dashboard for all projects"""
        try:
            # Count projects by status
            status_counts = {}
            for project in projects:
                status = project.get('status', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Calculate budget overview
            budget_total = sum(float(p.get('budget', 0)) for p in projects)
            expenses_total = sum(float(p.get('expenses', 0)) for p in projects)
            over_budget_projects = [p for p in projects if float(p.get('expenses', 0)) > float(p.get('budget', 0))]
            
            # Calculate remaining budget (ensure it's not negative for display purposes)
            remaining = max(0, budget_total - expenses_total)
            utilization_percentage = round((expenses_total / budget_total * 100) if budget_total else 0, 2)
            
            # Monthly expense forecast
            forecast_data = self._generate_forecast_data(projects)
            
            # Recent projects - sort by start date
            try:
                recent_projects = sorted(
                    projects, 
                    key=lambda p: datetime.strptime(p.get('start_date', '2000-01-01'), '%Y-%m-%d'),
                    reverse=True
                )[:5]
            except (ValueError, TypeError):
                # Fallback if date parsing fails
                recent_projects = projects[:5]
            
            # Properly format data as JSON strings for the template
            return {
                'projects_count': len(projects),
                'status_distribution': json.dumps(status_counts),
                'budget': {
                    'total': budget_total,
                    'expenses': expenses_total,
                    'remaining': remaining,
                    'utilization_percentage': utilization_percentage,
                    'over_budget_count': len(over_budget_projects)
                },
                'forecast': json.dumps(forecast_data),
                'recent_projects': recent_projects
            }
        except Exception as e:
            print(f"Error generating overview dashboard: {e}")
            return {
                'projects_count': 0,
                'status_distribution': json.dumps({}),
                'budget': {
                    'total': 0,
                    'expenses': 0,
                    'remaining': 0,
                    'utilization_percentage': 0,
                    'over_budget_count': 0
                },
                'forecast': json.dumps([]),
                'recent_projects': []
            }
    
    def _generate_forecast_data(self, projects):
        """Generate 6-month expense forecast data"""
        try:
            # Get current month and calculate forecast
            current_month = datetime.now().month
            current_year = datetime.now().year
            forecast_data = []
            
            # Calculate total project budget
            total_budget = sum(float(p.get('budget', 0)) for p in projects)
            
            # If no budget, return empty forecast
            if total_budget == 0:
                return []
            
            # Get active projects (for better forecast)
            active_projects = [p for p in projects if p.get('status') == 'active']
            
            # If no active projects, use all projects
            if not active_projects:
                active_projects = projects
            
            # Calculate monthly burn rate (simple model - distribute remaining budgets over next 6 months)
            remaining_budget = sum(max(0, float(p.get('budget', 0)) - float(p.get('expenses', 0))) for p in active_projects)
            monthly_burn_rate = remaining_budget / 6 if remaining_budget > 0 else total_budget / 12
            
            # Generate forecast for next 6 months
            for i in range(6):
                forecast_month = (current_month + i - 1) % 12 + 1  # Keep in range 1-12
                forecast_year = current_year + ((current_month + i) // 12)
                
                # Adjust burn rate with a simple model (higher in middle months)
                adjustment = 1 + (0.1 * (3 - abs(3 - i)))  # Peaks in the middle months
                forecast_value = monthly_burn_rate * adjustment
                
                forecast_data.append({
                    'month': datetime(forecast_year, forecast_month, 1).strftime('%b'),
                    'value': round(forecast_value, 2)
                })
            
            return forecast_data
        except Exception as e:
            print(f"Error generating forecast data: {e}")
            return []
    
    def _calculate_timeline_progress(self, project):
        """Calculate project timeline progress"""
        today = datetime.now().date()
        
        try:
            start_date = datetime.strptime(project.get('start_date', ''), '%Y-%m-%d').date()
            
            # Handle end_date (might be empty)
            end_date_str = project.get('end_date')
            if end_date_str and end_date_str.strip():
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            else:
                # If no end date, estimate 3 months from start
                end_date = start_date + timedelta(days=90)
            
            total_days = (end_date - start_date).days
            elapsed_days = (today - start_date).days if today > start_date else 0
            
            # Cap at 100%
            percentage = min(100, round((elapsed_days / total_days * 100) if total_days else 0))
            
            days_remaining = (end_date - today).days if end_date > today else 0
            status = "completed" if percentage >= 100 else "in_progress"
            
            return {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'elapsed_days': elapsed_days,
                'total_days': total_days,
                'days_remaining': days_remaining,
                'percentage': percentage,
                'status': status
            }
        except (ValueError, TypeError) as e:
            print(f"Error calculating timeline progress: {e}")
            # Return default values if dates can't be parsed
            return {
                'start_date': project.get('start_date', 'N/A'),
                'end_date': project.get('end_date', 'N/A'),
                'elapsed_days': 0,
                'total_days': 0,
                'days_remaining': 0,
                'percentage': 0,
                'status': 'unknown'
            }
    
    def _calculate_budget_utilization(self, project):
        """Calculate project budget utilization"""
        try:
            budget = float(project.get('budget', 0))
            expenses = float(project.get('expenses', 0))
            
            if budget > 0:
                percentage = round((expenses / budget * 100), 2)
                remaining = budget - expenses
                return {
                    'budget': budget,
                    'expenses': expenses,
                    'remaining': remaining,  # Correctly calculated remaining amount
                    'percentage': percentage,
                    'status': 'over_budget' if expenses > budget else 'under_budget'
                }
            return {
                'budget': budget,
                'expenses': expenses,
                'remaining': 0,
                'percentage': 0,
                'status': 'unknown'
            }
        except (ValueError, TypeError) as e:
            print(f"Error calculating budget utilization: {e}")
            return {
                'budget': 0,
                'expenses': 0,
                'remaining': 0,
                'percentage': 0,
                'status': 'unknown'
            }
    
    def _analyze_team_composition(self, members):
        """Analyze team composition by role"""
        try:
            role_counts = {}
            for member in members:
                role = member.get('role', 'Unknown')
                role_counts[role] = role_counts.get(role, 0) + 1
            
            return {
                'total_members': len(members),
                'role_distribution': role_counts,
                'members': members
            }
        except Exception as e:
            print(f"Error analyzing team composition: {e}")
            return {
                'total_members': 0,
                'role_distribution': {},
                'members': []
            }