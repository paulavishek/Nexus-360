import os
import openai
from django.conf import settings

class OpenAIClient:
    """
    Client for interacting with OpenAI API
    """
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
    
    # Update this method in chatbot/utils/openai_client.py

    def get_chatbot_response(self, prompt, project_data=None, history=None, sheet_context=None):
    """
    Get response from OpenAI API using GPT-4o-mini with improved error handling
    
    Args:
        prompt (str): User query
        project_data (dict): Project data to inform the chatbot
        history (list): Chat history for context
        sheet_context (str): Additional context about which sheet(s) are being queried
        
    Returns:
        str: Chatbot response
    """
        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key is not configured. Please check your .env file.")
        
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
        
        # Make the API call with timeout handling
        import time
        max_retries = 2
        retry_count = 0
        
        while retry_count <= max_retries:
            try:
                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    max_tokens=1000,
                    temperature=0.7,
                    timeout=15  # 15 second timeout
                )
                
                return response.choices[0].message.content
                
            except openai.APITimeoutError:
                if retry_count < max_retries:
                    retry_count += 1
                    time.sleep(1)  # Wait 1 second between retries
                    continue
                else:
                    raise TimeoutError("OpenAI API request timed out after multiple retries")
                    
            except openai.RateLimitError:
                raise Exception("OpenAI rate limit exceeded. Please try again later.")
                
            except openai.APIError as e:
                error_message = str(e)
                if "model_not_found" in error_message:
                    raise Exception("The specified OpenAI model 'gpt-4o-mini' was not found. Please check your configuration.")
                elif "context_length_exceeded" in error_message:
                    raise Exception("The conversation is too long for the model to process.")
                else:
                    raise Exception(f"OpenAI API error: {error_message}")
                    
            except Exception as e:
                raise Exception(f"Error with OpenAI API: {str(e)}")
        
    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        raise