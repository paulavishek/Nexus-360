import time
from .openai_client import OpenAIClient
from .gemini_client import GeminiClient
from .google_sheets import GoogleSheetsClient

class ChatbotService:
    """
    Main service for the project management chatbot with fallback strategy
    """
    def __init__(self):
        self.openai_client = OpenAIClient()
        self.gemini_client = GeminiClient()
        self.sheets_client = GoogleSheetsClient()
        
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
    
    def get_response(self, prompt, sheet_name=None, history=None):
        """
        Get chatbot response with fallback strategy
        
        Args:
            prompt (str): User query
            sheet_name (str, optional): Name of the specific sheet to query.
                                       If None, considers all sheets.
            history (list): Chat history for context
            
        Returns:
            dict: Response with source information
        """
        # Check if query is related to projects (if so, fetch project data)
        project_related = self._is_project_related_query(prompt)
        
        # Check if query specifies a particular sheet
        detected_sheet = self._detect_sheet_name_in_query(prompt)
        if detected_sheet:
            sheet_name = detected_sheet
            
        # Get data from specified sheet or all sheets
        project_data = self.get_project_data(sheet_name) if project_related else None
        
        # If sheet name is specified, add context about which sheet is being queried
        if project_data and sheet_name:
            sheet_context = f"You are providing information specifically from the '{sheet_name}' project sheet."
        elif project_data:
            available_sheets = self.sheets_client.get_available_sheet_names()
            if len(available_sheets) > 1:
                sheet_context = f"You are providing information from multiple project sheets: {', '.join(available_sheets)}. " \
                               f"When answering, specify which sheet each piece of information comes from."
            else:
                sheet_context = ""
        else:
            sheet_context = ""
        
        # Try OpenAI first
        try:
            response = self.openai_client.get_chatbot_response(prompt, project_data, history, sheet_context)
            return {
                'response': response,
                'source': 'openai',
                'sheet_name': sheet_name,
                'error': None
            }
        except Exception as e:
            print(f"OpenAI error: {e}")
            # Fall back to Gemini
            try:
                # Add a small delay before trying the fallback service
                time.sleep(0.5)
                response = self.gemini_client.get_chatbot_response(prompt, project_data, history, sheet_context)
                return {
                    'response': response,
                    'source': 'gemini',
                    'sheet_name': sheet_name,
                    'error': str(e)
                }
            except Exception as gemini_err:
                print(f"Gemini error: {gemini_err}")
                return {
                    'response': "I'm sorry, I'm having trouble connecting to my services right now. Please try again later.",
                    'source': 'error',
                    'sheet_name': None,
                    'error': str(gemini_err)
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