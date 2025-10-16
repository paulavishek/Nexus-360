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
        
    def get_chatbot_response(self, prompt, database_data=None, history=None, context=None, use_fallback=True):
        """
        Get response from Gemini API
        
        Args:
            prompt (str): User query
            database_data (dict): Database data to inform the chatbot
            history (list): Chat history for context
            context (str): Additional context for the chatbot
            use_fallback (bool): Whether to use fallback on errors (not used for Gemini, kept for compatibility)
            
        Returns:
            str: Chatbot response
        """
        try:
            # Create a system prompt with context that allows for both database and general knowledge questions
            system_message = """
            You are a helpful assistant that can answer both database-related questions and general knowledge questions.
            
            When responding to questions about the database, refer to the database information provided and be precise and specific.
            
            For general knowledge questions not covered by the database, you should provide helpful and accurate information based on your training.
            DO NOT refuse to answer general knowledge questions that aren't related to the database.
            
            Always be concise, professional, and helpful.
            """
            
            # Add context if provided
            if context:
                system_message += f"\n\n{context}"
            
            # Analyze the database data to determine its structure and content
            if database_data:
                system_message += "\nHere is the current database data to reference when answering database-related questions:\n"
                system_message += str(database_data)
                
                # Adding clear instruction about general knowledge
                system_message += "\n\nIMPORTANT: If the user asks a question that's not related to this database data, you should still answer it using your general knowledge. Don't refuse to answer just because the information isn't in the database."
            
            # Configure the model with parameters similar to OpenAI for consistency
            generation_config = {
                "temperature": 0.3,  # Lower temperature for more precise answers, matching OpenAI
                "max_output_tokens": 500,  # Matching the max_tokens we set for OpenAI
                "top_p": 0.95,  # Controls diversity
                "top_k": 40  # Limits vocabulary selections
            }
            
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
            
            # Configure the model - using the latest available Gemini model name with parameters
            model = genai.GenerativeModel(
                model_name='gemini-2.5-flash',  # Updated to use Gemini 2.5 Flash
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
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
            
            # Check if this is likely a general knowledge question
            is_general_knowledge = self._is_likely_general_knowledge(prompt, database_data)
            
            # Customize the message based on question type
            if is_general_knowledge:
                full_prompt = f"{system_message}\n\nThe following question appears to be a general knowledge question not related to the database. Please answer it using your training:\n\n{prompt}"
            else:
                full_prompt = f"{system_message}\n\n{prompt}"
                
            # Send message to Gemini
            response = chat_session.send_message(full_prompt)
            
            # Return the response text
            return response.text
            
        except Exception as e:
            print(f"Error with Gemini API: {e}")
            return f"I encountered an error while using my fallback AI service: {str(e)}. Please try again later."
    
    def _is_likely_general_knowledge(self, prompt, database_data):
        """
        Analyze the prompt to determine if it's likely to be a general knowledge question
        not related to the database
        """
        # Common general knowledge indicators
        general_knowledge_indicators = [
            "what is", "what are", "who is", "who was", "when was", "when did",
            "how does", "why does", "explain", "define", "tell me about"
        ]
        
        # Convert prompt to lowercase for easier matching
        prompt_lower = prompt.lower()
        
        # Database-related terms that might exist in the database
        database_related_terms = ["database", "data", "table", "record", "field", "project", 
                                  "status", "user", "id", "name", "date"]
        
        # Try to analyze database fields if database_data is provided
        database_terms = set()
        if database_data:
            try:
                # Extract potential field names and values from the database
                if isinstance(database_data, dict):
                    for key, value in database_data.items():
                        database_terms.add(key.lower())
                        if isinstance(value, dict):
                            for subkey in value.keys():
                                database_terms.add(subkey.lower())
                                
                                # If we have worksheets with records
                                if isinstance(value[subkey], list) and len(value[subkey]) > 0:
                                    # Add field names from the first record
                                    if isinstance(value[subkey][0], dict):
                                        for field in value[subkey][0].keys():
                                            database_terms.add(field.lower())
                                            
                                            # Add some values as potential search terms
                                            if isinstance(value[subkey][0][field], str):
                                                database_terms.add(value[subkey][0][field].lower())
            except:
                # Fallback to basic terms if we can't analyze the database
                pass
            
            # Add extracted terms to our database terms
            database_related_terms.extend(list(database_terms))
        
        # Check if any database term appears in the prompt
        for term in database_related_terms:
            if term in prompt_lower and len(term) > 2:  # Avoid short terms that might cause false positives
                return False  # Likely database related
                
        # Check for general knowledge indicators
        for indicator in general_knowledge_indicators:
            if prompt_lower.startswith(indicator):
                return True  # Likely general knowledge
                
        # Default case - hard to determine
        return False