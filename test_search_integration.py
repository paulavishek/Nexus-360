import os
import sys
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_chatbot.settings')
# Force SQLite for testing to avoid DB connection issues
os.environ['DB_TYPE'] = 'sqlite'
import django
django.setup()

from chatbot.utils.chatbot_service import ChatbotService

print('Testing Google Search integration in chatbot service...')

try:
    chatbot = ChatbotService()
    
    # Test with queries that should trigger search
    test_queries = [
        "What are the latest trends in 2025?",
        "Tell me about recent developments in AI",
        "What happened this week in the news?",
        "What's the current weather like?",
        "What are recent project management methodologies in 2025?"
    ]
    
    for query in test_queries:
        print(f'\n--- Testing query: "{query}" ---')
        
        # Check if query would trigger search
        is_search_query = chatbot._is_search_query(query)
        print(f'Would trigger search: {is_search_query}')
        
        if is_search_query:
            try:
                # Get search context
                search_context = chatbot._get_search_enhanced_context(query, max_results=2)
                if search_context:
                    print(f'Search context preview (first 200 chars): {search_context[:200]}...')
                    
                    # Check if it contains recent/current information
                    has_recent_info = any(term in search_context.lower() for term in ['2025', '2024', 'recent', 'latest', 'current', 'today', 'this week', 'this month'])
                    print(f'Contains recent/current information: {has_recent_info}')
                else:
                    print('No search context generated')
            except Exception as e:
                print(f'Error getting search context: {e}')
        
        print('-' * 50)
        
except Exception as e:
    print(f'Error testing chatbot service: {e}')
