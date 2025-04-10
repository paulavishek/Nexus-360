import time
from .openai_client import OpenAIClient
from .google_sheets import GoogleSheetsClient

class ChatbotService:
    """
    Main service for the chatbot with database integration
    """
    def __init__(self):
        self.openai_client = OpenAIClient()
        self.sheets_client = GoogleSheetsClient()
        
    def get_database_data(self):
        """
        Fetch data from the database (Google Sheets in this implementation)
        
        Returns:
            dict: Database data that can be used for chatbot context
        """
        try:
            # Get all available data that might be relevant for answering queries
            data = self.sheets_client.get_all_data()
            return data
        except Exception as e:
            print(f"Error fetching database data: {e}")
            return None

    def get_response(self, prompt, context=None, history=None):
        """
        Get chatbot response
        
        Args:
            prompt (str): User query
            context (dict, optional): Additional context for the chatbot
            history (list): Chat history for context
            
        Returns:
            dict: Response with source information
        """
        # Get database data to provide context for the chatbot
        try:
            database_data = self.get_database_data()
        except Exception as e:
            print(f"Error fetching database data: {e}")
            database_data = None
            # Return error message if we can't fetch the database data
            return {
                'response': f"I'm having trouble accessing the database. Please try again later. Error: {str(e)}",
                'source': 'error',
                'error': str(e)
            }
        
        # Build context for the chatbot
        context_text = ""
        if context:
            context_text += f"{context}\n"
            
        try:
            response = self.openai_client.get_chatbot_response(prompt, database_data, history, context_text)
            return {
                'response': response,
                'source': 'openai',
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
                    'error': error_message
                }
            
            # Handle other errors
            return {
                'response': "I'm sorry, I'm having trouble connecting to the AI service right now. Please try again later.",
                'source': 'error',
                'error': error_message
            }