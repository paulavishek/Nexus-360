import os
import time
import google.generativeai as genai
from django.conf import settings

class GeminiClient:
    """
    Client for interacting with Google Gemini API as a fallback when OpenAI is rate limited
    """
    def __init__(self):
        # Get API key from settings
        api_key = getattr(settings, 'GOOGLE_GEMINI_API_KEY', None)
        
        if not api_key:
            # Extract from environment variable if available
            api_key_line = next((line for line in open(os.path.join(settings.BASE_DIR, '.env')).readlines() 
                            if 'Gemini API' in line), None)
            if api_key_line:
                api_key = api_key_line.split('=')[1].strip()
        
        if not api_key:
            raise ValueError("Google Gemini API key is not configured.")
            
        # Configure the Gemini API client
        genai.configure(api_key=api_key)
        
    def get_chatbot_response(self, prompt, database_data=None, history=None, context=None):
        """
        Get response from Gemini API
        
        Args:
            prompt (str): User query
            database_data (dict): Database data to inform the chatbot
            history (list): Chat history for context
            context (str): Additional context for the chatbot
            
        Returns:
            str: Chatbot response
        """
        try:
            # Create a system prompt with context
            system_message = """
            You are a helpful assistant that provides information based on the connected database.
            You can answer questions about the data stored in the database and provide general information.
            Always be concise, professional, and helpful.
            """
            
            # Add context if provided
            if context:
                system_message += f"\n\n{context}"
            
            if database_data:
                system_message += "\nHere is the current database data to reference when answering questions:\n"
                system_message += str(database_data)
            
            # Configure the model
            model = genai.GenerativeModel('gemini-1.0-pro')
            
            # Format chat history for Gemini
            chat_session = model.start_chat(history=[])
            
            # Add chat history if provided
            if history:
                formatted_history = []
                for message in history:
                    if message["role"] == "user":
                        formatted_history.append({"role": "user", "parts": [message["content"]]})
                    else:
                        formatted_history.append({"role": "model", "parts": [message["content"]]})
                        
                chat_session = model.start_chat(history=formatted_history)
            
            # Send system prompt as initial context
            response = chat_session.send_message(system_message + "\n\n" + prompt)
            
            # Return the response text
            return response.text
            
        except Exception as e:
            print(f"Error with Gemini API: {e}")
            return f"I encountered an error while using my fallback AI service: {str(e)}. Please try again later."