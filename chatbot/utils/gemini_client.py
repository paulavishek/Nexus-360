import google.generativeai as genai
from django.conf import settings

class GeminiClient:
    """
    Client for interacting with Google Gemini API as fallback
    """
    def __init__(self):
        genai.configure(api_key=settings.GOOGLE_GEMINI_API_KEY)
    
    def get_chatbot_response(self, prompt, project_data=None, history=None, sheet_context=None):
        """
        Get response from Google Gemini model as fallback
        
        Args:
            prompt (str): User query
            project_data (dict): Project data to inform the chatbot
            history (list): Chat history for context
            sheet_context (str): Additional context about which sheet(s) are being queried
            
        Returns:
            str: Chatbot response
        """
        try:
            # Initialize the model (using Gemini Pro)
            model = genai.GenerativeModel('gemini-pro')
            
            # Prepare the content
            content = ""
            
            # Add context about the chatbot and project data
            system_instruction = """
            You are a helpful project management assistant that provides information about projects in the database.
            You can answer questions about projects, team members, budgets, and general project management advice.
            Always be concise, professional, and helpful.
            """
            
            content += system_instruction
            
            # Add sheet context if provided
            if sheet_context:
                content += f"\n\n{sheet_context}"
            
            if project_data:
                content += "\nHere is the current project data to reference when answering questions:\n"
                content += str(project_data)
            
            # Add chat history for context
            if history:
                content += "\n\nPrevious conversation:\n"
                for message in history:
                    role = "User" if message["role"] == "user" else "Assistant"
                    content += f"{role}: {message['content']}\n"
            
            # Add the user's current prompt
            content += f"\nUser query: {prompt}\n"
            
            # Make the API call
            response = model.generate_content(content)
            
            return response.text
        
        except Exception as e:
            print(f"Error with Google Gemini API: {e}")
            # Return a default response in case of error
            return "I'm sorry, I encountered an error processing your request. Please try again later."