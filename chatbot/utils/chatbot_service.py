import time
import random
from .openai_client import OpenAIClient
from .gemini_client import GeminiClient
from .google_sheets import GoogleSheetsClient
from .sql_database_client import SQLDatabaseClient
from .google_search import GoogleSearchClient
from django.conf import settings
import json
import pandas as pd
import logging

class ChatbotService:
    """
    Main service for the chatbot with database integration
    """
    def __init__(self):
        self.gemini_client = GeminiClient()
        self.openai_client = OpenAIClient()
        self.sheets_client = GoogleSheetsClient()
        self.sql_client = SQLDatabaseClient()
        self.search_client = GoogleSearchClient()
        self.rate_limit_retries = 3
        self.rate_limit_cooldown = 5  # seconds
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
    def get_database_data(self, use_cache=True):
        """
        Fetch data from the database (Google Sheets in this implementation)
        
        Args:
            use_cache (bool): Whether to use cached data if available. Set to False to force a fresh fetch.
            
        Returns:
            dict: Database data that can be used for chatbot context
        """
        # Check which data source to use based on configuration
        if hasattr(settings, 'USE_SQL_DATABASE') and settings.USE_SQL_DATABASE:
            return self.get_sql_database_data()
        else:
            # Default to Google Sheets if SQL is not configured
            return self.get_sheets_data(use_cache)
            
    def get_sheets_data(self, use_cache=True):
        """Fetch data from Google Sheets"""
        try:
            # Get all available data that might be relevant for answering queries
            data = self.sheets_client.get_all_data(use_cache=use_cache)
            return data
        except Exception as e:
            print(f"Error fetching Google Sheets data: {e}")
            return None
    
    def get_sql_database_data(self):
        """Fetch data structure from SQL database"""
        try:
            # Get database schema and table information
            db_info = self.sql_client.get_database_info()
            return db_info
        except Exception as e:
            print(f"Error fetching SQL database structure: {e}")
            return None
    
    def execute_sql_query(self, query, params=None):
        """
        Execute a SQL query and return results
        
        Args:
            query (str): SQL query to execute
            params (dict): Query parameters
            
        Returns:
            pandas.DataFrame: Query results
        """
        try:
            # Execute the query with safe mode enabled
            result = self.sql_client.execute_query(query, params, safe_mode=True)
            return result
        except Exception as e:
            print(f"Error executing SQL query: {e}")
            return pd.DataFrame({"error": [f"Error: {str(e)}"]})
            
    def clear_cache(self):
        """
        Clear the database cache to ensure fresh data is fetched next time
        
        Returns:
            bool: True if cache was successfully cleared, False otherwise
        """
        try:
            # Clear Google Sheets cache
            self.sheets_client.clear_cache()
            
            # Reset SQL table cache if applicable
            if hasattr(self.sql_client, '_tables'):
                self.sql_client._tables = None
                
            return True
        except Exception as e:
            print(f"Error clearing cache: {e}")
            return False

    def get_response(self, prompt, context=None, history=None, use_cache=True, sheet_name=None, preferred_model='gemini'):
        """
        Get chatbot response
        
        Args:
            prompt (str): User query
            context (dict, optional): Additional context for the chatbot
            history (list): Chat history for context
            use_cache (bool): Whether to use cached data. Set to False to force a fresh data fetch.
            sheet_name (str): Optional specific sheet/table name to focus on
            preferred_model (str): Preferred model to use ('gemini' or 'openai')
            
        Returns:
            dict: Response with source information
        """
        # Detect if this might be a query requiring SQL
        is_sql_query = self._is_sql_query(prompt)
        
        # Detect if this might benefit from a web search
        is_search_query = self._is_search_query(prompt)
        search_context = ""
        
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
            
        # If this looks like a query that would benefit from web search, get search results
        if is_search_query:
            try:
                print("Query might benefit from web search, fetching results...")
                search_context = self._get_search_enhanced_context(prompt)
            except Exception as e:
                print(f"Error fetching search results: {e}")
                # Continue without search results if there's an error
        
        # If this looks like a SQL query and we're using SQL database, try to execute it directly
        if is_sql_query and hasattr(settings, 'USE_SQL_DATABASE') and settings.USE_SQL_DATABASE:
            try:
                # For safety, let the AI model generate the actual SQL query
                # First, extract the query from the AI
                sql_query_request = f"""
                Based on the following request, generate a SQL query that is safe to execute:
                "{prompt}"
                
                Database schema: {json.dumps(database_data, indent=2)}
                
                Return ONLY the SQL query without any explanation or formatting, just the raw SQL statement.
                """
                
                # Use the model to generate a SQL query
                generated_query = self.gemini_client.get_chatbot_response(
                    sql_query_request, None, None, "You are a SQL query generator. Generate only SQL queries."
                )
                
                # Clean up the query (remove any backticks or markdown formatting)
                clean_query = self._extract_sql_from_response(generated_query)
                
                # If a specific table/sheet was requested, make sure it's part of the query
                if sheet_name and sheet_name.lower() not in clean_query.lower():
                    # Check if we should add a WHERE clause to filter by the sheet name
                    if 'where' not in clean_query.lower():
                        # Simple case: add WHERE for a table that matches the sheet name
                        if 'from' in clean_query.lower():
                            # Try to add a filter for this specific table
                            clean_query = clean_query.replace(
                                f"FROM {sheet_name}", 
                                f"FROM {sheet_name} WHERE {sheet_name}.name = '{sheet_name}'"
                            )
                
                # Execute the SQL query
                query_result = self.execute_sql_query(clean_query)
                
                # If the query was successful and returned results, format them nicely
                if not query_result.empty and "error" not in query_result.columns:
                    # Convert to markdown table or other readable format
                    result_md = self._dataframe_to_markdown(query_result)
                    
                    # Use AI to generate a natural language explanation of the results
                    explanation_request = f"""
                    Explain the following SQL query and its results in plain language:
                    
                    Query: {clean_query}
                    
                    Results:
                    {result_md}
                    
                    Provide a concise summary that a non-technical person would understand.
                    """
                    
                    explanation = self.gemini_client.get_chatbot_response(
                        explanation_request, None, None, "You are explaining SQL query results."
                    )
                    
                    # Return combined result with the query, data, and explanation
                    response = f"""
                    {explanation}
                    
                    **SQL Query Used:**
                    ```sql
                    {clean_query}
                    ```
                    
                    **Query Results:**
                    {result_md}
                    """
                    
                    return {
                        'response': response,
                        'source': 'sql-query',
                        'sheet_name': sheet_name,
                        'error': None
                    }
                else:
                    # Query had an error, fall back to normal chatbot response
                    error = query_result["error"][0] if "error" in query_result.columns else "No results returned"
                    print(f"SQL query error: {error}")
            except Exception as e:
                print(f"Error executing SQL query: {e}")
                # Continue to standard AI response
        
        # Build context for the chatbot
        context_text = ""
        if context:
            context_text += f"{context}\n"
            
        # Add search results to context if available
        if search_context:
            context_text += f"\n{search_context}\n"
            
        try:
            # Select the appropriate client based on preferred model
            if preferred_model == 'openai':
                primary_client = self.openai_client
                fallback_client = self.gemini_client
                primary_model_name = 'openai'
                fallback_model_name = 'gemini'
            else:
                primary_client = self.gemini_client
                fallback_client = self.openai_client
                primary_model_name = 'gemini'
                fallback_model_name = 'openai'
            
            # Modify prompt if search results were used
            enhanced_prompt = prompt
            if search_context:
                # No need to modify the prompt, as we'll be passing the search results as context
                source = f"{primary_model_name}-with-search"
            else:
                source = primary_model_name
                
            # Use the selected model WITHOUT its built-in fallback
            response = primary_client.get_chatbot_response(
                enhanced_prompt, 
                database_data, 
                history, 
                context_text,
                use_fallback=False  # Disable built-in fallback
            )
            
            return {
                'response': response,
                'source': source,
                'sheet_name': sheet_name,
                'error': None
            }
        except Exception as e:
            error_message = str(e)
            print(f"Primary model ({primary_model_name}) error: {e}")
            
            # Only fall back if it's a rate limit or temporary error, not for API key issues
            if "api key" in error_message.lower() or "authentication" in error_message.lower():
                return {
                    'response': f"There's an issue with the {primary_model_name.upper()} API configuration. Please check your API key settings.",
                    'source': 'error',
                    'error': error_message
                }
            
            # Try fallback model with proper labeling
            print(f"Attempting fallback to {fallback_model_name}")
            return self._try_fallback_model(
                prompt, 
                database_data, 
                history, 
                context_text, 
                error_message,
                fallback_client,
                fallback_model_name
            )
    
    def _is_sql_query(self, prompt):
        """
        Determine if the prompt appears to be a SQL query request
        
        Args:
            prompt (str): User query
            
        Returns:
            bool: True if it looks like a SQL query request
        """
        # Check for SQL query indicators
        prompt_lower = prompt.lower()
        
        # Check for common SQL query terms/patterns
        sql_indicators = [
            "select", "query", "join", "where", "group by", "filter", 
            "fetch", "retrieve", "show me data", "search for", "find all",
            "database", "table", "sql", "count"
        ]
        
        # Check for question patterns typical of database queries
        question_patterns = [
            "how many", "list all", "show me", "which", "what are", "who has", 
            "find", "search for", "where can i find"
        ]
        
        # Calculate a score based on presence of indicators
        score = 0
        for indicator in sql_indicators:
            if indicator in prompt_lower:
                score += 1
        
        for pattern in question_patterns:
            if pattern in prompt_lower:
                score += 0.5
                
        return score >= 1.5  # Threshold for being considered a likely SQL query
    
    def _extract_sql_from_response(self, response):
        """Extract a SQL query from an AI response, removing any markdown formatting"""
        # Try to extract SQL from markdown code blocks first
        import re
        sql_pattern = r"```sql\s*([\s\S]*?)\s*```"
        matches = re.findall(sql_pattern, response)
        
        if matches:
            return matches[0].strip()
        
        # Try generic code blocks if no SQL blocks found
        code_pattern = r"```\s*([\s\S]*?)\s*```"
        matches = re.findall(code_pattern, response)
        
        if matches:
            return matches[0].strip()
            
        # If no code blocks, just use the raw response but clean it up
        # Remove common intro phrases
        cleaned = re.sub(r"(?i)^(here'?s?( is)?|the)? (a |the )?sql( query)?( would be)?:?", "", response.strip())
        
        return cleaned.strip()
        
    def _dataframe_to_markdown(self, df, max_rows=20):
        """Convert a pandas DataFrame to a markdown table"""
        if df.empty:
            return "*No results*"
            
        # Limit to max_rows
        if len(df) > max_rows:
            df = df.head(max_rows)
            footer = f"\n\n*Showing {max_rows} of {len(df)} results*"
        else:
            footer = ""
            
        # Convert to markdown
        md_table = df.to_markdown(index=False)
        return md_table + footer
    
    def _try_fallback_model(self, prompt, database_data, history, context_text, error_message, fallback_client, fallback_model_name):
        """
        Try fallback model with exponential backoff for rate limit errors
        
        Args:
            prompt (str): User query
            database_data (dict): Database data
            history (list): Chat history
            context_text (str): Additional context
            error_message (str): Error message from the first model
            fallback_client: The client to use for fallback
            fallback_model_name (str): Name of the fallback model
            
        Returns:
            dict: Response with source information
        """
        max_retries = self.rate_limit_retries
        base_delay = self.rate_limit_cooldown
        
        for attempt in range(max_retries):
            try:
                print(f"Using fallback model {fallback_model_name} (attempt {attempt + 1}/{max_retries})")
                fallback_response = fallback_client.get_chatbot_response(
                    prompt, 
                    database_data, 
                    history, 
                    context_text,
                    use_fallback=False  # Disable nested fallback
                )
                return {
                    'response': fallback_response,
                    'source': fallback_model_name,
                    'error': None
                }
            except Exception as fallback_error:
                error_str = str(fallback_error).lower()
                
                # Check if it's a rate limit error
                if "rate limit" in error_str or "too many requests" in error_str or "429" in error_str:
                    # If this is the last attempt, return error
                    if attempt == max_retries - 1:
                        return {
                            'response': "I'm sorry, both AI services are currently experiencing high demand. Please try again in a few minutes.",
                            'source': 'error',
                            'error': "All models experiencing rate limits"
                        }
                    
                    # Calculate delay with jitter (random variation)
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    print(f"Rate limit exceeded, retrying in {delay:.2f} seconds (attempt {attempt + 1}/{max_retries})")
                    time.sleep(delay)
                else:
                    # Not a rate limit error, just a regular error
                    print(f"Fallback model error: {fallback_error}")
                    return {
                        'response': f"I'm sorry, I'm having trouble processing your request right now. Please try again with a simpler query.",
                        'source': 'error',
                        'error': f"Error: {str(fallback_error)}"
                    }
        
        # If we've exhausted all retries
        return {
            'response': "I'm experiencing connectivity issues. Please try again later.",
            'source': 'error',
            'error': "Max retries exceeded"
        }
    
    def _is_search_query(self, prompt):
        """
        Determine if the prompt would benefit from a web search
        
        Args:
            prompt (str): User query
            
        Returns:
            bool: True if the query likely needs real-time or up-to-date information
        """
        prompt_lower = prompt.lower()
        
        # Enhanced keywords indicating need for recent information
        search_indicators = [
            # Time-based indicators
            "latest", "recent", "current", "news", "today", "yesterday", 
            "this week", "this month", "this year", "update", "updated",
            
            # Action/event indicators  
            "happened", "trending", "released", "announced", "launch", "launched",
            "breaking", "event", "events", 
            
            # Market/finance indicators
            "stock", "price", "prices", "market", 
            
            # Technology indicators
            "covid", "pandemic", "election", "weather",
            
            # Year indicators for recent information
            "2024", "2025", # Assuming current year is 2025 or queries relate to it
            
            # Additional time indicators (high priority additions)
            "now", "currently", "at the moment", "right now", "as of",
            "up to date", "up-to-date", "real time", "real-time",
            "live", "immediate", "instantly",
            
            # Development/business indicators
            "developments", "progress", "advancement", "innovation",
            "breakthrough", "update", "revision", "changes",
            
            # News/media indicators  
            "report", "reports", "article", "study", "research",
            "publication", "findings", "discovery", "announcement",

            # New general keywords
            "define", "explain", "who is", "what is", "how to", "why do",
            "compare", "difference between", "pros and cons",
            "best practice", "tutorial", "guide", "statistics", "data on"
        ]
        
        # Enhanced question patterns that often need web search
        question_patterns = [
            # Original patterns
            "what is the latest", "how recent", "when did", "what happened",
            "tell me about", "is there any news", "what's new", "what are some recent",
            
            # Additional patterns (high priority additions)
            "what's happening", "what's going on", "any updates on",
            "current status of", "latest news about", "recent developments in",
            "what's the current", "how is", "what are the current trends",
            "latest information on", "recent updates about", "current state of",
            "what's the situation with", "any recent news about",
            "current events", "breaking news", "recent reports on"
        ]
        
        # Calculate a score based on presence of indicators
        score = 0
        for indicator in search_indicators:
            if indicator in prompt_lower:
                score += 1
                
        for pattern in question_patterns:
            if pattern in prompt_lower:
                score += 0.7
                  # If database already has the information, we might not need a search
        database_focused = "in the database" in prompt_lower or "in our data" in prompt_lower or "in the sheet" in prompt_lower
        if database_focused:
            score -= 1
            
        return score >= 1.0  # Threshold for when search is likely helpful
    
    def _get_search_enhanced_context(self, prompt, max_results=3):
        """
        Get web search results to enhance the context for an AI response
        
        Args:
            prompt (str): User query
            max_results (int): Maximum number of search results
            
        Returns:
            str: Web search results formatted as context
        """
        try:
            # Get search context with caching enabled
            search_context = self.search_client.get_search_context(prompt, max_results=max_results, use_cache=True)
            
            # Add instructions for the model
            search_context += "\n\nPlease use this information to help answer the user's question accurately. " \
                            "When citing sources, include the full source information including title and URL in parentheses. " \
                            "If the search results are not relevant, rely on your existing knowledge instead."
                            
            return search_context
        except Exception as e:
            error_msg = f"Error getting search context: {e}"
            self.logger.error(error_msg)
            return ""
    
    def get_search_metrics(self, date_str=None):
        """
        Get search metrics for the current date or specified date
        
        Args:
            date_str (str): Date string in YYYYMMDD format, defaults to today
            
        Returns:
            dict: Search metrics including success rate, cache hit rate, etc.
        """
        try:
            metrics = self.search_client.get_search_metrics(date_str)
            
            # Calculate derived metrics
            if metrics['total_searches'] > 0:
                metrics['success_rate'] = (metrics['successful_searches'] / metrics['total_searches']) * 100
                metrics['cache_hit_rate'] = (metrics['cached_searches'] / metrics['total_searches']) * 100
                
                if metrics['successful_searches'] > metrics['cached_searches']:
                    api_calls = metrics['successful_searches'] - metrics['cached_searches']
                    metrics['average_response_time'] = metrics['total_response_time'] / api_calls if api_calls > 0 else 0
                else:
                    metrics['average_response_time'] = 0
            else:
                metrics['success_rate'] = 0
                metrics['cache_hit_rate'] = 0
                metrics['average_response_time'] = 0
                
            return metrics
        except Exception as e:
            self.logger.error(f"Error getting search metrics: {e}")
            return {
                'total_searches': 0,
                'successful_searches': 0,
                'failed_searches': 0,
                'cached_searches': 0,
                'success_rate': 0,
                'cache_hit_rate': 0,
                'average_response_time': 0
            }
    
    def clear_search_cache(self):
        """
        Clear search cache and return status
        
        Returns:
            bool: True if cache was cleared successfully
        """
        try:
            return self.search_client.clear_search_cache()
        except Exception as e:
            self.logger.error(f"Error clearing search cache: {e}")
            return False