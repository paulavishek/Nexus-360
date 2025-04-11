import time
import random
from .openai_client import OpenAIClient
from .gemini_client import GeminiClient
from .google_sheets import GoogleSheetsClient

class ChatbotService:
    """
    Main service for the chatbot with database integration
    """
    def __init__(self):
        # Use Gemini as primary model and OpenAI as fallback (reversed from before)
        self.gemini_client = GeminiClient()
        self.openai_client = OpenAIClient()
        self.sheets_client = GoogleSheetsClient()
        self.rate_limit_retries = 3
        self.rate_limit_cooldown = 5  # seconds
        
    def get_database_data(self, use_cache=True):
        """
        Fetch data from the database (Google Sheets in this implementation)
        
        Args:
            use_cache (bool): Whether to use cached data if available. Set to False to force a fresh fetch.
            
        Returns:
            dict: Database data that can be used for chatbot context
        """
        try:
            # Get all available data that might be relevant for answering queries
            data = self.sheets_client.get_all_data(use_cache=use_cache)
            return data
        except Exception as e:
            print(f"Error fetching database data: {e}")
            return None
            
    def clear_cache(self):
        """
        Clear the database cache to ensure fresh data is fetched next time
        
        Returns:
            bool: True if cache was successfully cleared, False otherwise
        """
        try:
            self.sheets_client.clear_cache()
            return True
        except Exception as e:
            print(f"Error clearing cache: {e}")
            return False

    def get_response(self, prompt, context=None, history=None, use_cache=True):
        """
        Get chatbot response
        
        Args:
            prompt (str): User query
            context (dict, optional): Additional context for the chatbot
            history (list): Chat history for context
            use_cache (bool): Whether to use cached data. Set to False to force a fresh data fetch.
            
        Returns:
            dict: Response with source information
        """
        # Get database data to provide context for the chatbot
        try:
            database_data = self.get_database_data(use_cache=use_cache)
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
            # Use Gemini as the primary model now
            response = self.gemini_client.get_chatbot_response(prompt, database_data, history, context_text)
            
            return {
                'response': response,
                'source': 'gemini',  # Changed from 'openai' to 'gemini'
                'error': None
            }
        except Exception as e:
            error_message = str(e)
            print(f"Gemini client error: {e}")
            
            # Fall back to OpenAI if Gemini fails
            return self._try_openai_with_backoff(prompt, database_data, history, context_text, error_message)
    
    def _try_openai_with_backoff(self, prompt, database_data, history, context_text, primary_error_message):
        """
        Try OpenAI with exponential backoff for rate limit errors
        
        Args:
            prompt (str): User query
            database_data (dict): Database data
            history (list): Chat history
            context_text (str): Additional context
            primary_error_message (str): Error message from the primary model
            
        Returns:
            dict: Response with source information
        """
        max_retries = self.rate_limit_retries
        base_delay = self.rate_limit_cooldown
        
        for attempt in range(max_retries):
            try:
                print(f"Using OpenAI fallback (attempt {attempt + 1}/{max_retries})")
                fallback_response = self.openai_client.get_chatbot_response(prompt, database_data, history, context_text)
                return {
                    'response': fallback_response,
                    'source': 'openai-fallback',  # Mark this as the fallback model
                    'error': None
                }
            except Exception as openai_error:
                error_str = str(openai_error).lower()
                
                # Check if it's a rate limit error
                if "rate limit" in error_str or "too many requests" in error_str or "429" in error_str:
                    # If this is the last attempt, return the error
                    if attempt == max_retries - 1:
                        print("OpenAI rate limit exceeded, using Gemini fallback")
                        try:
                            # Try Gemini again with a simplified prompt
                            simplified_prompt = f"Please answer this question concisely: {prompt}"
                            simplified_response = self.gemini_client.get_chatbot_response(
                                simplified_prompt, database_data, None, context_text
                            )
                            return {
                                'response': simplified_response,
                                'source': 'gemini-retry',
                                'error': None
                            }
                        except Exception as gemini_retry_error:
                            # Both models failed, return a friendly error
                            return {
                                'response': "I'm sorry, both AI services are currently experiencing high demand. Please try again in a few minutes.",
                                'source': 'error',
                                'error': f"Primary error: {primary_error_message}, Fallback errors: Rate limits exceeded"
                            }
                    
                    # Calculate delay with jitter (random variation)
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    print(f"OpenAI rate limit exceeded, retrying in {delay:.2f} seconds (attempt {attempt + 1}/{max_retries})")
                    time.sleep(delay)
                else:
                    # Not a rate limit error, just a regular error
                    print(f"OpenAI fallback error: {openai_error}")
                    return {
                        'response': f"I'm sorry, I'm having trouble processing your request right now. Please try again with a simpler query.",
                        'source': 'error',
                        'error': f"Primary error: {primary_error_message}, Fallback error: {str(openai_error)}"
                    }
        
        # If we've exhausted all retries
        return {
            'response': "I'm experiencing connectivity issues. Please try again later.",
            'source': 'error',
            'error': f"Max retries exceeded for both models"
        }