import os
import time
import random
import openai
from django.conf import settings

class OpenAIClient:
    """
    Client for interacting with OpenAI API with improved rate limit handling
    """
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        # Default retry settings
        self.max_retries = 5
        self.initial_retry_delay = 1  # Start with 1 second
        self.max_retry_delay = 60     # Maximum delay of 60 seconds
        
    def get_chatbot_response(self, prompt, database_data=None, history=None, context=None):
        """
        Get response from OpenAI API using GPT-4o-mini with improved error handling
        and exponential backoff for rate limits
        
        Args:
            prompt (str): User query
            database_data (dict): Database data to inform the chatbot
            history (list): Chat history for context
            context (str): Additional context for the chatbot
            
        Returns:
            str: Chatbot response
        """
        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key is not configured. Please check your .env file.")
        
        # Prepare messages
        messages = []
        
        # Add system message with context about the chatbot and database data
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
        
        # Try with exponential backoff for rate limits
        retries = 0
        while retries <= self.max_retries:
            try:
                # Try to call the API
                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    max_tokens=1000,
                    temperature=0.7,
                    timeout=15  # 15 second timeout
                )
                
                return response.choices[0].message.content
                
            except openai.APITimeoutError:
                if retries < self.max_retries:
                    retries += 1
                    delay = min(self.initial_retry_delay * (2 ** retries) + random.uniform(0, 1), self.max_retry_delay)
                    print(f"OpenAI timeout, retrying in {delay:.2f} seconds (attempt {retries}/{self.max_retries})")
                    time.sleep(delay)
                    continue
                else:
                    raise TimeoutError(f"OpenAI API request timed out after {self.max_retries} retries")
                    
            except openai.RateLimitError:
                if retries < self.max_retries:
                    retries += 1
                    delay = min(self.initial_retry_delay * (2 ** retries) + random.uniform(0, 1), self.max_retry_delay)
                    print(f"OpenAI rate limit exceeded, retrying in {delay:.2f} seconds (attempt {retries}/{self.max_retries})")
                    time.sleep(delay)
                    continue
                else:
                    # If we've exhausted retries, fall back to a default response
                    fallback_msg = (
                        "I'm currently experiencing high demand and can't process your request right now. "
                        "Please try again in a few minutes. In the meantime, you can try asking a simpler question "
                        "or refreshing the page."
                    )
                    return fallback_msg
                    
            except openai.APIError as e:
                error_message = str(e)
                if "model_not_found" in error_message:
                    return "I'm having trouble connecting to my AI service. The model 'gpt-4o-mini' may not be available. Please try a different model or contact support."
                elif "context_length_exceeded" in error_message:
                    return "Your conversation is too long for me to process. Please try starting a new conversation or ask a shorter question."
                else:
                    if retries < self.max_retries:
                        retries += 1
                        delay = min(self.initial_retry_delay * (2 ** retries) + random.uniform(0, 1), self.max_retry_delay)
                        print(f"OpenAI API error, retrying in {delay:.2f} seconds (attempt {retries}/{self.max_retries}): {error_message}")
                        time.sleep(delay)
                        continue
                    else:
                        return f"I encountered an error while processing your request: {error_message}. Please try again later."
                        
            except Exception as e:
                print(f"Unexpected error with OpenAI API: {e}")
                return "I'm having technical difficulties right now. Please try again later or contact support if this persists."
                
        # This should rarely happen since we return from the loop
        return "I couldn't process your request after multiple attempts. Please try again later."