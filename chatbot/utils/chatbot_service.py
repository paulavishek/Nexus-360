import time
from .openai_client import OpenAIClient
from .google_sheets import GoogleSheetsClient
from .dashboard_service import DashboardService

class ChatbotService:
    """
    Main service for the project management chatbot
    """
    def __init__(self):
        self.openai_client = OpenAIClient()
        self.sheets_client = GoogleSheetsClient()
        self.dashboard_service = DashboardService(self.sheets_client)
        
    def get_project_data(self, sheet_name=None):
        """
        Fetch project data from Google Sheets
        
        Args:
            sheet_name (str, optional): Name of the specific sheet to query. 
                                      If None, gets data from all sheets.
        """
        if sheet_name:
            projects = self.sheets_client.get_all_projects(sheet_name)
            members = self.sheets_client.get_project_members(sheet_name=sheet_name)
            budget_stats = self.sheets_client.get_budget_statistics(sheet_name)
        else:
            projects = self.sheets_client.get_all_projects_from_all_sheets()
            members = self.sheets_client.get_all_members_from_all_sheets()
            budget_stats = self.sheets_client.get_budget_statistics()
        
        return {
            'projects': projects,
            'members': members,
            'budget_statistics': budget_stats
        }

    def _is_project_related_query(self, query):
        """
        Determine if the query is related to projects
        
        Args:
            query (str): User query
            
        Returns:
            bool: True if query is project-related, False otherwise
        """
        project_keywords = [
            'project', 'projects', 'team', 'member', 'members', 'budget', 'cost',
            'expense', 'expenses', 'over budget', 'under budget', 'status',
            'active', 'completed', 'on hold', 'cancelled', 'team size',
            'timeline', 'deadline', 'start date', 'end date', 'sheet', 'sheets'
        ]
        
        query_lower = query.lower()
        for keyword in project_keywords:
            if keyword in query_lower:
                return True
        
        return False
        
    def _detect_sheet_name_in_query(self, query):
        """
        Detect if the user is asking about a specific sheet by name
        
        Args:
            query (str): User query
            
        Returns:
            str or None: Sheet name if detected, None otherwise
        """
        available_sheets = self.sheets_client.get_available_sheet_names()
        query_lower = query.lower()
        
        # Look for patterns like "in the X sheet" or "from sheet Y"
        for sheet_name in available_sheets:
            sheet_lower = sheet_name.lower()
            patterns = [
                f"in {sheet_lower} sheet",
                f"from {sheet_lower} sheet",
                f"in the {sheet_lower} sheet",
                f"from the {sheet_lower} sheet",
                f"in {sheet_lower}",
                f"from {sheet_lower}",
                f"{sheet_lower} projects",
                f"{sheet_lower} data"
            ]
            
            for pattern in patterns:
                if pattern in query_lower:
                    return sheet_name
        
        return None

    def _is_dashboard_request(self, query):
        """
        Determine if the query is requesting a dashboard
        
        Args:
            query (str): User query
            
        Returns:
            bool: True if query is requesting a dashboard, False otherwise
        """
        dashboard_keywords = [
            'dashboard', 'visualize', 'visualization', 'chart', 'graph',
            'show me', 'display', 'create a', 'generate a', 'information radiator',
            'stats', 'statistics', 'metrics', 'kpi', 'overview'
        ]
        
        # Additional keywords that strongly suggest dashboard intent when paired with project terms
        context_keywords = {
            'project': ['create', 'generate', 'make', 'build', 'show', 'visualize'],
            'budget': ['chart', 'breakdown', 'distribution', 'allocation'],
            'timeline': ['progress', 'gantt', 'schedule', 'milestone'],
            'team': ['composition', 'roles', 'structure', 'organization']
        }
        
        query_lower = query.lower()
        
        # Check for direct dashboard keywords
        for keyword in dashboard_keywords:
            if keyword in query_lower:
                return True
        
        # Check for context-specific dashboard requests
        for context, keywords in context_keywords.items():
            if context in query_lower:
                for keyword in keywords:
                    if keyword in query_lower:
                        return True
        
        return False

    def get_response(self, prompt, sheet_name=None, history=None):
        """
        Get chatbot response
        
        Args:
            prompt (str): User query
            sheet_name (str, optional): Name of the specific sheet to query.
                                        If None, considers all sheets.
            history (list): Chat history for context
            
        Returns:
            dict: Response with source information
        """
        # Check if query is requesting a dashboard
        dashboard_request = self._is_dashboard_request(prompt)
        if dashboard_request:
            # Detect if query is about a specific project
            project_name = None
            
            # Simple extraction - in a real implementation, you would use NLP
            # to more accurately extract project names from queries
            project_related = self._is_project_related_query(prompt)
            if project_related:
                # Get all projects to compare against
                try:
                    projects = self.sheets_client.get_all_projects_from_all_sheets()
                    project_names = [p.get('name', '').lower() for p in projects]
                    
                    # Look for project names in the query
                    words = prompt.lower().split()
                    for i in range(len(words) - 1):
                        potential_name = words[i] + ' ' + words[i+1]  # Check for two-word project names
                        if potential_name in project_names:
                            project_name = potential_name
                            break
                    
                    if not project_name:  # Check for single-word project names
                        for word in words:
                            if word in project_names:
                                project_name = word
                                break
                except Exception as e:
                    print(f"Error extracting project name: {e}")
            
            # Return instructions for dashboard access
            dashboard_url = f"/dashboard/{'project/' + project_name if project_name else ''}"
            dashboard_type = "project" if project_name else "overview"
            
            return {
                'response': f"I've prepared a {dashboard_type} dashboard for you. You can access it at {dashboard_url} or click the button below.",
                'source': 'dashboard',
                'sheet_name': sheet_name,
                'dashboard_url': dashboard_url,
                'dashboard_type': dashboard_type,
                'project_name': project_name
            }
        
        # Check if detected sheet name in query should override the provided sheet_name
        detected_sheet = self._detect_sheet_name_in_query(prompt)
        if detected_sheet:
            sheet_name = detected_sheet
            
        # Check if query is related to projects (if so, fetch project data)
        project_related = self._is_project_related_query(prompt)
        
        # Get data from specified sheet or all sheets
        try:
            project_data = self.get_project_data(sheet_name) if project_related else None
        except Exception as e:
            print(f"Error fetching project data: {e}")
            project_data = None
            # Return error message if we can't even fetch project data
            return {
                'response': f"I'm having trouble accessing the project database. Please try again later. Error: {str(e)}",
                'source': 'error',
                'sheet_name': sheet_name,
                'error': str(e)
            }
        
        # If sheet name is specified, add context about which sheet is being queried
        if project_data and sheet_name:
            sheet_context = f"You are providing information specifically from the '{sheet_name}' project sheet."
        elif project_data:
            available_sheets = self.sheets_client.get_available_sheet_names()
            if len(available_sheets) > 1:
                sheet_context = (
                    f"You are providing information from multiple project sheets: {', '.join(available_sheets)}. "
                    "When answering, specify which sheet each piece of information comes from."
                )
            else:
                sheet_context = ""
        else:
            sheet_context = ""
        
        try:
            response = self.openai_client.get_chatbot_response(prompt, project_data, history, sheet_context)
            return {
                'response': response,
                'source': 'openai',
                'sheet_name': sheet_name,
                'error': None
            }
        except Exception as e:
            error_message = str(e)
            print(f"OpenAI error: {e}")
            
            # Check if this is an API key or configuration error
            if "API key" in error_message or "configuration" in error_message or "not configured" in error_message:
                return {
                    'response': "The OpenAI service is not properly configured. Please contact the administrator to set up the API key correctly.",
                    'source': 'error',
                    'sheet_name': None,
                    'error': error_message
                }
            
            # Handle other errors
            return {
                'response': "I'm sorry, I'm having trouble connecting to the AI service right now. Please try again later.",
                'source': 'error',
                'sheet_name': None,
                'error': error_message
            }