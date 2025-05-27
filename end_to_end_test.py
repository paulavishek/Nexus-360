import os
os.environ['DB_TYPE'] = 'sqlite'
os.environ['DJANGO_SETTINGS_MODULE'] = 'project_chatbot.settings'
import django
django.setup()

from chatbot.utils.chatbot_service import ChatbotService
import json

print("=== END-TO-END CHATBOT WITH GOOGLE SEARCH TEST ===")
print("Testing if the chatbot properly integrates Google Search for recent information")
print()

try:
    chatbot_service = ChatbotService()
    
    # Test query that should trigger Google Search
    test_query = "What are the latest trends in project management for 2025?"
    
    print(f"Test Query: '{test_query}'")
    print("-" * 60)
    
    # Check if this query would trigger search
    is_search_query = chatbot_service._is_search_query(test_query)
    print(f"✅ Query triggers search detection: {is_search_query}")
    
    if is_search_query:
        # Test the search context generation
        try:
            search_context = chatbot_service._get_search_enhanced_context(test_query, max_results=2)
            print(f"✅ Search context generated successfully")
            print(f"Context length: {len(search_context)} characters")
            
            # Check for key elements in search context
            has_sources = '[Source' in search_context
            has_urls = 'URL:' in search_context
            has_2025 = '2025' in search_context
            has_citations = 'citing sources' in search_context.lower()
            
            print(f"✅ Contains source references: {has_sources}")
            print(f"✅ Contains URLs: {has_urls}")
            print(f"✅ Contains 2025 information: {has_2025}")
            print(f"✅ Contains citation instructions: {has_citations}")
            
            print("\nSample of search context:")
            print(search_context[:300] + "..." if len(search_context) > 300 else search_context)
            
        except Exception as e:
            print(f"❌ Error generating search context: {e}")
    
    print("\n" + "="*60)
    print("TESTING COMPLETE CHATBOT RESPONSE")
    print("="*60)
    
    # Test a complete response (but don't actually call the AI to avoid costs)
    print("Note: Skipping actual AI response to avoid API costs")
    print("The integration chain is: Query -> Search Detection -> Google Search -> Context -> AI Model")
    
    # Test another query type
    print(f"\nTesting database-focused query (should NOT trigger search):")
    db_query = "Show me projects in our database"
    is_db_search = chatbot_service._is_search_query(db_query)
    print(f"Database query triggers search: {is_db_search} (should be False)")
    
except Exception as e:
    print(f"❌ Error in end-to-end test: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("FINAL ASSESSMENT")
print("="*80)
