import requests
import os
from django.conf import settings
import json
import time
import random
import logging
from django.core.cache import cache
import hashlib
from datetime import datetime

class GoogleSearchClient:
    """
    Client for Google Custom Search API integration with caching and monitoring
    """
    def __init__(self):
        # Get API key and Search Engine ID from settings or environment variables
        self.api_key = getattr(settings, 'GOOGLE_SEARCH_API_KEY', os.environ.get('GOOGLE_SEARCH_API_KEY'))
        self.search_engine_id = getattr(settings, 'GOOGLE_SEARCH_ENGINE_ID', os.environ.get('GOOGLE_SEARCH_ENGINE_ID'))
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        self.max_results = 5  # Default number of results to return
        self.rate_limit_retries = getattr(settings, 'GOOGLE_SEARCH_RATE_LIMIT_RETRIES', 3)
        self.rate_limit_cooldown = getattr(settings, 'GOOGLE_SEARCH_RATE_LIMIT_COOLDOWN', 2)  # seconds
        self.cache_timeout = getattr(settings, 'GOOGLE_SEARCH_CACHE_TIMEOUT', 1800)  # 30 minutes cache timeout by default
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Cache key prefix for search results
        self.cache_prefix = "google_search"

    def _get_cache_key(self, query, num_results, search_type):
        """
        Generate a cache key for the search query
        
        Args:
            query (str): Search query
            num_results (int): Number of results
            search_type (str): Type of search
            
        Returns:
            str: Cache key
        """
        # Normalize query for better cache hits (e.g., lowercasing, removing extra spaces)
        normalized_query = ' '.join(query.lower().split())
        key_data = f"{normalized_query}_{num_results}_{search_type or 'web'}"
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"{self.cache_prefix}_{key_hash}"

    def _log_search_metrics(self, query, success=True, error_msg=None, response_time=None, cached=False, status_code=None):
        """
        Log search metrics for monitoring
        
        Args:
            query (str): Search query
            success (bool): Whether the search was successful
            error_msg (str): Error message if search failed
            response_time (float): Response time in seconds
            cached (bool): Whether result was from cache
            status_code (int): HTTP status code from the API response
        """
        timestamp = datetime.now().isoformat()
        log_level = logging.INFO if success else logging.ERROR
        status_text = "CACHED" if cached else ("SUCCESS" if success else "FAILED")
        
        log_message = f"Google Search [{status_text}] - Query: '{query[:100]}...'"
        if response_time is not None:
            log_message += f" - Response time: {response_time:.2f}s"
        if error_msg:
            log_message += f" - Error: {error_msg}"
        if status_code:
            log_message += f" - Status Code: {status_code}"
        log_message += f" - Time: {timestamp}"
        
        self.logger.log(log_level, log_message)
            
        # Store metrics in cache for dashboard/analytics
        metrics_key = f"search_metrics_{datetime.now().strftime('%Y%m%d')}"
        try:
            daily_metrics = cache.get(metrics_key, {
                'total_searches': 0,
                'successful_searches': 0,
                'failed_searches': 0,
                'cached_searches': 0,
                'total_response_time': 0.0,
                'error_details': [] # New: Store details of errors
            })
            
            daily_metrics['total_searches'] += 1
            if success:
                daily_metrics['successful_searches'] += 1
                if cached:
                    daily_metrics['cached_searches'] += 1
                elif response_time is not None:
                    daily_metrics['total_response_time'] += response_time
            else:
                daily_metrics['failed_searches'] += 1
                if error_msg: # Log detailed error
                    daily_metrics['error_details'].append({
                        'timestamp': timestamp,
                        'query': query,
                        'error': error_msg,
                        'status_code': status_code
                    })
                
            cache.set(metrics_key, daily_metrics, 86400)  # Store for 24 hours
        except Exception as e:
            self.logger.error(f"Error storing search metrics: {e}")

    def search(self, query, num_results=None, search_type=None, use_cache=True):
        """
        Perform a Google search query with caching and monitoring
        
        Args:
            query (str): Search query
            num_results (int): Number of results to return (max 10)
            search_type (str): Type of search ('image' for image search)
            use_cache (bool): Whether to use cached results if available
            
        Returns:
            list: Formatted search results or None if an error occurs
        """
        start_time = time.time()
        
        if not self.api_key or not self.search_engine_id:
            error_msg = "Google Search API key and Search Engine ID must be configured"
            self._log_search_metrics(query, success=False, error_msg=error_msg)
            # Instead of raising ValueError, return None or an empty list to allow graceful failure
            return None 
            
        num = min(num_results or self.max_results, 10)  # Google limits to 10 results per query
        
        # Check cache first
        if use_cache:
            cache_key = self._get_cache_key(query, num, search_type)
            cached_result = cache.get(cache_key)
            if cached_result:
                self._log_search_metrics(query, success=True, cached=True, response_time=(time.time() - start_time))
                return cached_result
        
        params = {
            'key': self.api_key,
            'cx': self.search_engine_id,
            'q': query,
            'num': num
        }
        
        if search_type:
            params['searchType'] = search_type
        
        # Retry logic for rate limiting and transient errors
        for attempt in range(self.rate_limit_retries):
            try:
                response = requests.get(self.base_url, params=params, timeout=10) # Added timeout
                response.raise_for_status() # Raises HTTPError for bad responses (4XX or 5XX)
                
                search_results = response.json()
                formatted_results = self._format_search_results(search_results)
                
                # Cache the results
                if use_cache and formatted_results: # Only cache if results are not empty
                    cache_key = self._get_cache_key(query, num, search_type)
                    cache.set(cache_key, formatted_results, self.cache_timeout)
                
                response_time_val = time.time() - start_time
                self._log_search_metrics(query, success=True, response_time=response_time_val, status_code=response.status_code)
                return formatted_results
                
            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code
                error_message = f"HTTP {status_code}: {str(e)}"
                if status_code == 429:  # Rate limit error
                    if attempt < self.rate_limit_retries - 1:
                        delay = self.rate_limit_cooldown * (2 ** attempt) + random.uniform(0, 1)
                        self.logger.warning(f"Google Search API rate limit hit (attempt {attempt + 1}/{self.rate_limit_retries}), retrying in {delay:.2f} seconds. Query: '{query[:50]}...' ")
                        time.sleep(delay)
                        continue
                    else:
                        error_message = f"Google Search API rate limit exceeded after {self.rate_limit_retries} retries. Query: '{query[:50]}...'"
                        self._log_search_metrics(query, success=False, error_msg=error_message, status_code=status_code, response_time=(time.time() - start_time))
                        return None # Return None after exhausting retries
                else:
                    # For other HTTP errors, log and return None (or handle specific codes as needed)
                    self._log_search_metrics(query, success=False, error_msg=error_message, status_code=status_code, response_time=(time.time() - start_time))
                    return None
            except requests.exceptions.RequestException as e: # Catch other request errors (e.g., timeout, connection error)
                error_message = f"RequestException: {str(e)}"
                self._log_search_metrics(query, success=False, error_msg=error_message, response_time=(time.time() - start_time))
                # Log and return None for non-HTTP errors during the request
                if attempt < self.rate_limit_retries - 1:
                    delay = self.rate_limit_cooldown * (2 ** attempt) + random.uniform(0, 1)
                    self.logger.warning(f"Google Search request error (attempt {attempt + 1}/{self.rate_limit_retries}), retrying in {delay:.2f} seconds. Query: '{query[:50]}...' Error: {error_message}")
                    time.sleep(delay)
                    continue
                else:
                    self._log_search_metrics(query, success=False, error_msg=f"Google Search failed after {self.rate_limit_retries} retries. Last error: {error_message}", response_time=(time.time() - start_time))
                    return None
                
        # Fallback if all retries fail for reasons not caught above (should be rare)
        final_error_msg = f"Google Search failed for query '{query[:50]}...' after all retries."
        self._log_search_metrics(query, success=False, error_msg=final_error_msg, response_time=(time.time() - start_time))
        return None

    def _format_search_results(self, raw_results):
        """
        Format raw Google Search API results into a more usable structure
        
        Args:
            raw_results (dict): Raw API response
            
        Returns:
            list: Formatted search results
        """
        formatted_results = []
        
        if 'items' not in raw_results:
            return formatted_results
            
        for item in raw_results['items']:
            result = {
                'title': item.get('title', ''),
                'link': item.get('link', ''),
                'snippet': item.get('snippet', ''),
                'source': 'google_search',
            }
            
            # Add image info if available
            if 'pagemap' in item and 'cse_image' in item['pagemap']:
                result['image_url'] = item['pagemap']['cse_image'][0].get('src', '')
                
            formatted_results.append(result)
            
        return formatted_results
        
    def get_search_context(self, query, max_results=3, use_cache=True):
        """
        Get search results formatted as context for the chatbot model
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results to include in context
            use_cache (bool): Whether to use cached results if available
            
        Returns:
            str: Formatted context from search results
        """
        try:
            # Get search results
            results = self.search(query, num_results=max_results, use_cache=use_cache)
            
            if not results:
                return "No relevant search results found."
                
            # Format results as context
            context = "Here is information from recent web searches:\n\n"
            
            for i, result in enumerate(results):
                context += f"[Source {i+1}] {result['title']}\n"
                context += f"URL: {result['link']}\n"
                context += f"Excerpt: {result['snippet']}\n\n"
                
            # Add a section for source references
            context += "\nWhen citing sources in your response, please include the full source information as follows:\n"
            context += "For example, instead of just saying [Source 1], say [Source 1: Title of the Source (URL)].\n\n"
            
            # List sources for easy reference
            context += "Sources for reference:\n"
            for i, result in enumerate(results):
                context += f"[Source {i+1}: {result['title']} ({result['link']})]\n"
            
            return context
            
        except Exception as e:
            error_msg = f"Error retrieving search results: {str(e)}"
            self.logger.error(f"Error getting search context: {e}")
            return error_msg
    
    def get_search_metrics(self, date_str=None):
        """
        Get search metrics for monitoring dashboard
        
        Args:
            date_str (str): Date string in YYYYMMDD format, defaults to today
            
        Returns:
            dict: Search metrics for the specified date
        """
        if not date_str:
            date_str = datetime.now().strftime('%Y%m%d')
            
        metrics_key = f"search_metrics_{date_str}"
        metrics = cache.get(metrics_key, {
            'total_searches': 0,
            'successful_searches': 0,
            'failed_searches': 0,
            'cached_searches': 0,
            'total_response_time': 0.0,
            'average_response_time': 0.0, # Will be calculated
            'success_rate': 0.0, # Will be calculated
            'cache_hit_rate': 0.0, # Will be calculated
            'error_details': [] # Include error details
        })

        # Calculate derived metrics if not already present or need recalculation
        if metrics['total_searches'] > 0:
            metrics['success_rate'] = (metrics['successful_searches'] / metrics['total_searches']) * 100
            metrics['cache_hit_rate'] = (metrics['cached_searches'] / metrics['total_searches']) * 100
            
            # Calculate average response time for non-cached successful searches
            non_cached_successful_searches = metrics['successful_searches'] - metrics['cached_searches']
            if non_cached_successful_searches > 0 and metrics['total_response_time'] > 0:
                metrics['average_response_time'] = metrics['total_response_time'] / non_cached_successful_searches
            else:
                metrics['average_response_time'] = 0.0
        else:
            metrics['success_rate'] = 0.0
            metrics['cache_hit_rate'] = 0.0
            metrics['average_response_time'] = 0.0
            
        return metrics

    def clear_search_cache(self, query: str = None, num_results: int = None, search_type: str = None):
        """
        Clear specific cached search results or all search cache if no specific query is provided.

        Args:
            query (str, optional): Specific search query to clear from cache.
            num_results (int, optional): Number of results for the specific query.
            search_type (str, optional): Type of search for the specific query.

        Returns:
            bool: True if cache was cleared successfully, False otherwise.
        """
        try:
            if query and num_results is not None:
                cache_key = self._get_cache_key(query, num_results, search_type)
                cache.delete(cache_key)
                self.logger.info(f"Cleared specific search cache for key: {cache_key}")
            else:
                # Clear all keys with the google_search prefix
                # This requires iterating if `delete_many` with pattern is not directly supported
                # or a more specific cache backend feature.
                # For LocMemCache, a full clear is simple, but for others, more care is needed.
                # Assuming a simple `cache.clear()` for now if specific deletion is too complex for the backend.
                keys_to_delete = []
                # This is a placeholder for iterating keys if your cache backend allows it.
                # For Django's default LocMemCache, there isn't a direct way to list keys by prefix without introspection.
                # If using Redis or Memcached, you'd use their respective commands.
                # As a fallback, or if a full clear is acceptable in this context:
                # cache.clear() # Clears ENTIRE cache - use with extreme caution in production
                # For now, let's assume we can't list keys easily and only specific deletion is implemented.
                # If a full clear is intended, it should be explicit.
                # self.logger.info("Full search cache clear requested but not implemented without pattern matching. "
                #                 "Only specific query clearing is supported or a full application cache clear.")
                # Fallback to clearing all cache if no specific query is given and backend doesn't support prefix deletion easily.
                # This is a simplification. In a real app, you'd want to be more careful.
                # For now, we will only support specific key deletion or no-op for general clear.
                if query is None and num_results is None and search_type is None:
                    # This is a placeholder. Ideally, you'd iterate and delete keys with the prefix.
                    # For now, we'll log that a full clear of search cache isn't granularly supported here.
                    self.logger.warning("Attempted to clear all search cache, but this operation should be more specific or use a cache backend that supports prefix deletion. No keys were deleted by this general call.")
                    return False # Indicate that the operation wasn't fully performed as a general clear.

            return True
        except Exception as e:
            self.logger.error(f"Error clearing search cache: {e}")
            return False