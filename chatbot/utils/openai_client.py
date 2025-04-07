import os
import openai
from django.conf import settings

class OpenAIClient:
    """
    Client for interacting with OpenAI API
    """
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
    
    def get_chatbot_response(self, prompt, project_data=None, history=None, sheet_context=None):
        """
        Get response from OpenAI API using GPT-4o-mini
        
        Args:
            prompt (str): User query
            project_data (dict): Project data to inform the chatbot
            history (list): Chat history for context
            sheet_context (str): Additional context about which sheet(s) are being queried
            
        Returns:
            str: Chatbot response
        """
        try:
            # Prepare messages
            messages = []
            
            # Add system message with context about the chatbot and project data
            system_message = """
            You are a helpful project management assistant that provides information about projects in the database.
            You can answer questions about projects, team members, budgets, and general project management advice.
            Always be concise, professional, and helpful.
            """
            
            # Add sheet context if provided
            if sheet_context:
                system_message += f"\n\n{sheet_context}"
            
            if project_data:
                system_message += "\nHere is the current project data to reference when answering questions:\n"
                system_message += str(project_data)
            
            messages.append({"role": "system", "content": system_message})
            
            # Add chat history for context if provided
            if history:
                for message in history:
                    messages.append({
                        "role": message["role"],
                        "content": message["content"]
                    })
            
            # Add the user's current prompt
            messages.append({"role": "user", "content": prompt})
            
            # Make the API call
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            print(f"Error with OpenAI API: {e}")
            # Return a default response in case of error
            return "I'm sorry, I encountered an error processing your request. Please try again later."