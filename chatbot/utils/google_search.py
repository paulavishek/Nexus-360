import requests
import os
from django.conf import settings
import json
import time
import random

class GoogleSearchClient:
    """
    Client for Google Custom Search API integration
    """
    def __init__(self):
        # Get API key and Search Engine ID from settings or environment variables
        self.api_key = getattr(settings, 'GOOGLE_SEARCH_API_KEY', os.environ.get('GOOGLE_SEARCH_API_KEY'))
        self.search_engine_id = getattr(settings, 'GOOGLE_SEARCH_ENGINE_ID', os.environ.get('GOOGLE_SEARCH_ENGINE_ID'))
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        self.max_results = 5  # Default number of results to return
        self.rate_limit_retries = 3
        self.rate_limit_cooldown = 2  # seconds
        
    def search(self, query, num_results=None, search_type=None):
        """
        Perform a Google search query
        
        Args:
            query (str): Search query
            num_results (int): Number of results to return (max 10)
            search_type (str): Type of search ('image' for image search)
            
        Returns:
            dict: Search results with source links and snippets
        """
        if not self.api_key or not self.search_engine_id:
            raise ValueError("Google Search API key and Search Engine ID must be configured")
            
        num = min(num_results or self.max_results, 10)  # Google limits to 10 results per query
        
        params = {
            'key': self.api_key,
            'cx': self.search_engine_id,
            'q': query,
            'num': num
        }
        
        if search_type:
            params['searchType'] = search_type
        
        # Retry logic for rate limiting
        for attempt in range(self.rate_limit_retries):
            try:
                response = requests.get(self.base_url, params=params)
                response.raise_for_status()
                
                search_results = response.json()
                return self._format_search_results(search_results)
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:  # Rate limit error
                    delay = self.rate_limit_cooldown * (2 ** attempt) + random.uniform(0, 1)
                    print(f"Google Search API rate limit hit, retrying in {delay:.2f} seconds")
                    time.sleep(delay)
                    continue
                else:
                    raise
            except Exception as e:
                print(f"Google Search API error: {e}")
                raise
                
        # If we've exhausted all retries
        raise Exception("Google Search API rate limit exceeded after multiple retries")
    
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
        
    def get_search_context(self, query, max_results=3):
        """
        Get search results formatted as context for the chatbot model
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results to include in context
            
        Returns:
            str: Formatted context from search results
        """
        try:
            # Get search results
            results = self.search(query, num_results=max_results)
            
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
            print(f"Error getting search context: {e}")
            return f"Error retrieving search results: {str(e)}"