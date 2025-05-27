import os
import sys
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_chatbot.settings')
import django
django.setup()

from chatbot.utils.google_search import GoogleSearchClient
from django.conf import settings

print('Checking Google Search configuration...')
print(f'GOOGLE_SEARCH_API_KEY configured: {bool(getattr(settings, "GOOGLE_SEARCH_API_KEY", ""))}')
print(f'GOOGLE_SEARCH_ENGINE_ID configured: {bool(getattr(settings, "GOOGLE_SEARCH_ENGINE_ID", ""))}')
print(f'ENABLE_WEB_SEARCH: {getattr(settings, "ENABLE_WEB_SEARCH", False)}')

try:
    client = GoogleSearchClient()
    print(f'API Key exists: {bool(client.api_key)}')
    print(f'Search Engine ID exists: {bool(client.search_engine_id)}')
    
    if client.api_key and client.search_engine_id:
        print('\nTesting Google Search with a simple query...')
        # Test with a query that should return recent results
        results = client.search('current date today May 27 2025', num_results=2)
        if results:
            print(f'Search successful! Found {len(results)} results:')
            for i, result in enumerate(results[:2]):
                print(f'  {i+1}. {result["title"][:80]}...')
                print(f'      URL: {result["link"]}')
                print(f'      Snippet: {result["snippet"][:100]}...')
        else:
            print('Search returned no results')
    else:
        print('Google Search API is not properly configured')
        
except Exception as e:
    print(f'Error testing Google Search: {e}')
