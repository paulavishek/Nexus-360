import os
import time
import random
import openai
from django.conf import settings
from .gemini_client import GeminiClient

class OpenAIClient:
    """
    Client for interacting with OpenAI API with improved rate limit handling
    and Google Gemini fallback
    """
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        # Default retry settings
        self.max_retries = 5
        self.initial_retry_delay = 1  # Start with 1 second
        self.max_retry_delay = 60     # Maximum delay of 60 seconds
        
        # Initialize Gemini client for fallback
        try:
            self.gemini_client = GeminiClient()
            self.gemini_available = True
        except Exception as e:
            print(f"Gemini client initialization error: {e}")
            self.gemini_available = False
        
    def get_chatbot_response(self, prompt, database_data=None, history=None, context=None):
        """
        Get response from OpenAI API using GPT-4o-mini with improved error handling
        and exponential backoff for rate limits. Falls back to Gemini if necessary.
        
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
        Be precise, specific, and concise in your answers. Focus on facts from the database when available.
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
                # Try to call the API with reduced temperature and max_tokens as requested
                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    max_tokens=500,  # Reduced from 1000 to 500 to save costs
                    temperature=0.3,  # Reduced from 0.7 to 0.3 for more precise answers
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
                    # Try Gemini fallback after exhausting OpenAI retries
                    return self._use_gemini_fallback(prompt, database_data, history, context, 
                                                   "OpenAI API request timed out")
                    
            except openai.RateLimitError:
                if retries < self.max_retries:
                    retries += 1
                    delay = min(self.initial_retry_delay * (2 ** retries) + random.uniform(0, 1), self.max_retry_delay)
                    print(f"OpenAI rate limit exceeded, retrying in {delay:.2f} seconds (attempt {retries}/{self.max_retries})")
                    time.sleep(delay)
                    continue
                else:
                    # Try Gemini fallback for rate limit errors
                    return self._use_gemini_fallback(prompt, database_data, history, context, 
                                                   "OpenAI rate limit exceeded")
                    
            except openai.APIError as e:
                error_message = str(e)
                if "model_not_found" in error_message:
                    return self._use_gemini_fallback(prompt, database_data, history, context, 
                                                   "OpenAI model not found")
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
                        return self._use_gemini_fallback(prompt, database_data, history, context, error_message)
                        
            except Exception as e:
                print(f"Unexpected error with OpenAI API: {e}")
                return self._use_gemini_fallback(prompt, database_data, history, context, str(e))
                
        # This should rarely happen since we return from the loop
        return self._use_gemini_fallback(prompt, database_data, history, context, 
                                       "Maximum retries exceeded")
    
    def _use_gemini_fallback(self, prompt, database_data, history, context, error_reason):
        """
        Use Gemini as a fallback when OpenAI is unavailable
        
        Args:
            prompt (str): User query
            database_data (dict): Database data to inform the chatbot
            history (list): Chat history for context
            context (str): Additional context for the chatbot
            error_reason (str): The reason for falling back to Gemini
            
        Returns:
            str: Chatbot response
        """
        print(f"Using Gemini fallback due to OpenAI error: {error_reason}")
        
        if not self.gemini_available:
            return (
                f"I'm currently experiencing issues with my primary AI service ({error_reason}). "
                "Unfortunately, the backup service is also not available. "
                "Please try again in a few minutes or contact support if this persists."
            )
        
        try:
            # Attempt to use Gemini as a fallback
            response = self.gemini_client.get_chatbot_response(prompt, database_data, history, context)
            return f"{response}\n\n(Answered using Google Gemini 2.5-Flash as backup due to OpenAI being temporarily unavailable)"
        except Exception as e:
            print(f"Gemini fallback error: {e}")
            return (
                f"I'm currently experiencing issues with both my primary and backup AI services. "
                "Please try again in a few minutes or contact support if this persists."
            )