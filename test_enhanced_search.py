import os
import sys
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_chatbot.settings')
os.environ['DB_TYPE'] = 'sqlite'
import django
django.setup()

from chatbot.utils.google_search import GoogleSearchClient
from chatbot.utils.chatbot_service import ChatbotService
import time

print("=== ENHANCED GOOGLE SEARCH INTEGRATION TEST ===")
print("Testing the three high-priority improvements:")
print("1. Enhanced search trigger keywords")
print("2. Basic caching for performance")
print("3. Search failure monitoring")
print()

def test_enhanced_keywords():
    """Test the enhanced search trigger keywords"""
    print("1. TESTING ENHANCED SEARCH TRIGGER KEYWORDS")
    print("-" * 60)
    
    chatbot = ChatbotService()
    
    # Test queries with original keywords
    original_keywords_tests = [
        "What are the latest trends in 2025?",
        "Tell me about recent developments",
        "What happened today in the news?"
    ]
    
    # Test queries with NEW enhanced keywords
    enhanced_keywords_tests = [
        "What's happening right now in AI?",  # "right now", "what's happening"
        "Any updates on the current market situation?",  # "updates", "current"
        "What's the current status of electric vehicles?",  # "current status"
        "Recent developments in renewable energy",  # "developments"
        "Breaking news about space exploration",  # "breaking news"
        "Latest research findings on climate change",  # "research", "findings"
        "What are the current trends in remote work?",  # "current trends"
        "Real-time updates on cryptocurrency prices"  # "real-time"
    ]
    
    print("Testing original trigger keywords:")
    for query in original_keywords_tests:
        is_search = chatbot._is_search_query(query)
        print(f"  ✅ '{query}' -> Triggers search: {is_search}")
    
    print("\nTesting NEW enhanced trigger keywords:")
    enhanced_triggers = 0
    for query in enhanced_keywords_tests:
        is_search = chatbot._is_search_query(query)
        if is_search:
            enhanced_triggers += 1
        print(f"  {'✅' if is_search else '❌'} '{query}' -> Triggers search: {is_search}")
    
    print(f"\nEnhanced keyword detection: {enhanced_triggers}/{len(enhanced_keywords_tests)} queries triggered search")
    return enhanced_triggers >= len(enhanced_keywords_tests) * 0.8  # 80% success rate

def test_caching_performance():
    """Test the caching functionality"""
    print("\n2. TESTING CACHING FOR PERFORMANCE")
    print("-" * 60)
    
    try:
        client = GoogleSearchClient()
        test_query = "current AI trends 2025"
        
        # First search (should hit API)
        print("First search (should hit API)...")
        start_time = time.time()
        results1 = client.search(test_query, num_results=2, use_cache=True)
        first_time = time.time() - start_time
        print(f"  First search completed in {first_time:.2f} seconds")
        print(f"  Results returned: {len(results1)}")
        
        # Second search (should use cache)
        print("\nSecond search (should use cache)...")
        start_time = time.time()
        results2 = client.search(test_query, num_results=2, use_cache=True)
        second_time = time.time() - start_time
        print(f"  Cached search completed in {second_time:.2f} seconds")
        print(f"  Results returned: {len(results2)}")
        
        # Third search (bypass cache)
        print("\nThird search (bypassing cache)...")
        start_time = time.time()
        results3 = client.search(test_query, num_results=2, use_cache=False)
        third_time = time.time() - start_time
        print(f"  Non-cached search completed in {third_time:.2f} seconds")
        
        # Verify caching works
        cache_faster = second_time < first_time * 0.5  # Cache should be at least 50% faster
        results_consistent = len(results1) == len(results2)
        
        print(f"\n✅ Cache performance improvement: {cache_faster}")
        print(f"✅ Results consistency: {results_consistent}")
        print(f"   First search: {first_time:.2f}s, Cached: {second_time:.2f}s, Non-cached: {third_time:.2f}s")
        
        return cache_faster and results_consistent
        
    except Exception as e:
        print(f"❌ Caching test failed: {e}")
        return False

def test_search_monitoring():
    """Test the search failure monitoring and metrics"""
    print("\n3. TESTING SEARCH FAILURE MONITORING")
    print("-" * 60)
    
    try:
        chatbot = ChatbotService()
        client = GoogleSearchClient()
        
        # Test valid search with monitoring
        print("Testing successful search monitoring...")
        try:
            results = client.search("test monitoring query", num_results=1)
            print(f"✅ Successful search completed with {len(results)} results")
        except Exception as e:
            print(f"⚠️  Search failed but should be logged: {e}")
        
        # Get metrics
        print("\nRetrieving search metrics...")
        metrics = chatbot.get_search_metrics()
        print(f"✅ Metrics retrieved: {metrics}")
        
        # Test if metrics contain expected fields
        expected_fields = ['total_searches', 'successful_searches', 'failed_searches', 
                          'cached_searches', 'success_rate', 'cache_hit_rate']
        
        has_all_fields = all(field in metrics for field in expected_fields)
        print(f"✅ All expected metric fields present: {has_all_fields}")
        
        # Test with invalid API credentials (to trigger failure monitoring)
        print("\nTesting failure monitoring with invalid search...")
        temp_client = GoogleSearchClient()
        original_api_key = temp_client.api_key
        temp_client.api_key = "invalid_key_for_testing"
        
        try:
            temp_client.search("test failure", num_results=1)
            print("❌ Expected failure did not occur")
            failure_logged = False
        except Exception as e:
            print(f"✅ Expected failure occurred and should be logged: {str(e)[:100]}...")
            failure_logged = True
        
        # Restore original API key
        temp_client.api_key = original_api_key
        
        return has_all_fields and failure_logged
        
    except Exception as e:
        print(f"❌ Monitoring test failed: {e}")
        return False

def test_end_to_end_integration():
    """Test the complete enhanced integration"""
    print("\n4. END-TO-END INTEGRATION TEST")
    print("-" * 60)
    
    try:
        chatbot = ChatbotService()
        
        # Test with a query that should use enhanced keywords and caching
        test_query = "What are the current developments in artificial intelligence research?"
        
        print(f"Testing query: '{test_query}'")
        
        # Check if enhanced keywords trigger search
        is_search = chatbot._is_search_query(test_query)
        print(f"✅ Enhanced keywords trigger search: {is_search}")
        
        if is_search:
            # Test search context with caching
            print("Getting search-enhanced context...")
            start_time = time.time()
            context = chatbot._get_search_enhanced_context(test_query, max_results=2)
            end_time = time.time()
            
            has_context = len(context) > 100
            has_sources = '[Source' in context
            has_urls = 'URL:' in context
            
            print(f"✅ Search context generated: {has_context}")
            print(f"✅ Contains source references: {has_sources}")
            print(f"✅ Contains URLs: {has_urls}")
            print(f"✅ Response time: {end_time - start_time:.2f} seconds")
            
            return is_search and has_context and has_sources and has_urls
        else:
            print("❌ Enhanced keywords did not trigger search")
            return False
            
    except Exception as e:
        print(f"❌ End-to-end test failed: {e}")
        return False

# Run all tests
print("Starting comprehensive enhancement tests...\n")

test_results = []
test_results.append(("Enhanced Keywords", test_enhanced_keywords()))
test_results.append(("Caching Performance", test_caching_performance()))
test_results.append(("Search Monitoring", test_search_monitoring()))
test_results.append(("End-to-End Integration", test_end_to_end_integration()))

print("\n" + "="*80)
print("ENHANCEMENT TEST RESULTS")
print("="*80)

all_passed = True
for test_name, result in test_results:
    status = "✅ PASSED" if result else "❌ FAILED"
    print(f"{test_name:25} {status}")
    if not result:
        all_passed = False

print("\n" + "="*80)
if all_passed:
    print("🎉 ALL ENHANCEMENTS SUCCESSFULLY IMPLEMENTED!")
    print("The high-priority improvements are working correctly:")
    print("✅ Enhanced search trigger keywords")
    print("✅ Basic caching for performance")  
    print("✅ Search failure monitoring")
else:
    print("⚠️  Some enhancements need attention. Check the test results above.")

print("\nCheck the logs/google_search.log file for detailed search monitoring logs.")
print("="*80)
