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
    
    def _generate_single_project_dashboard(self, project, members):
        """Generate dashboard for a single project"""
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
    
    def _generate_overview_dashboard(self, projects):
        """Generate overview dashboard for all projects"""
        # Count projects by status
        status_counts = {}
        for project in projects:
            status = project.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Calculate budget overview
        budget_total = sum(float(p.get('budget', 0)) for p in projects)
        expenses_total = sum(float(p.get('expenses', 0)) for p in projects)
        over_budget_projects = [p for p in projects if float(p.get('expenses', 0)) > float(p.get('budget', 0))]
        
        # Monthly expense forecast (simplified example)
        current_month = datetime.now().month
        forecast_data = []
        for month in range(current_month, current_month + 6):
            # Simple forecast - actual would be more complex
            forecast_month = (month - 1) % 12 + 1  # Keep in range 1-12
            forecast_value = expenses_total / 6  # Simple even distribution
            forecast_data.append({
                'month': datetime(2025, forecast_month, 1).strftime('%b'),
                'value': round(forecast_value, 2)
            })
        
        return {
            'projects_count': len(projects),
            'status_distribution': status_counts,
            'budget': {
                'total': budget_total,
                'expenses': expenses_total,
                'remaining': budget_total - expenses_total,
                'utilization_percentage': round((expenses_total / budget_total * 100) if budget_total else 0, 2),
                'over_budget_count': len(over_budget_projects)
            },
            'forecast': forecast_data,
            'recent_projects': sorted(projects, key=lambda p: p.get('start_date', '2000-01-01'), reverse=True)[:5]
        }
    
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
        except (ValueError, TypeError):
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
        budget = float(project.get('budget', 0))
        expenses = float(project.get('expenses', 0))
        
        if budget > 0:
            percentage = round((expenses / budget * 100), 2)
            return {
                'budget': budget,
                'expenses': expenses,
                'remaining': budget - expenses,
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
    
    def _analyze_team_composition(self, members):
        """Analyze team composition by role"""
        role_counts = {}
        for member in members:
            role = member.get('role', 'Unknown')
            role_counts[role] = role_counts.get(role, 0) + 1
        
        return {
            'total_members': len(members),
            'role_distribution': role_counts,
            'members': members
        }