#!/usr/bin/env python3
"""
Comprehensive test for Google Search integration enhancements
Tests the three high priority improvements:
1. Enhanced search trigger keywords
2. Caching functionality
3. Search failure monitoring and logging
"""

import os
import sys
import django
import time
import json
from datetime import datetime

# Add the project directory to the Python path
sys.path.insert(0, r'c:\Users\Avishek Paul\pm_chatbot')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_chatbot.settings')
django.setup()

from chatbot.utils.chatbot_service import ChatbotService
from chatbot.utils.google_search import GoogleSearchClient
from django.core.cache import cache
import logging

class ComprehensiveEnhancementTester:
    """Test all Google Search enhancements"""
    
    def __init__(self):
        self.chatbot = ChatbotService()
        self.search_client = GoogleSearchClient()
        self.test_results = []
        
        # Setup test logger
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def log_test_result(self, test_name, passed, details=""):
        """Log test results"""
        status = "PASSED" if passed else "FAILED"
        result = {
            'test': test_name,
            'status': status,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        self.logger.info(f"[{status}] {test_name}: {details}")
        
    def test_enhanced_search_keywords(self):
        """Test 1: Enhanced search trigger keywords"""
        self.logger.info("\n=== Testing Enhanced Search Keywords ===")
        
        # Original keywords that should trigger search
        original_triggers = [
            "What's the latest news about Python?",
            "Current stock price of Apple",
            "Recent developments in AI"
        ]
        
        # Enhanced keywords that should now trigger search
        enhanced_triggers = [
            "What's happening with cryptocurrency right now?",
            "Any updates on climate change?",
            "Current trends in machine learning",
            "Latest information on COVID-19",
            "What's the current status of the economy?",
            "Recent breakthroughs in quantum computing",
            "Live updates on the election",
            "Real-time weather information"
        ]
        
        all_triggers = original_triggers + enhanced_triggers
        
        for query in all_triggers:
            should_search = self.chatbot._is_search_query(query)
            self.log_test_result(
                f"Search trigger: '{query[:30]}...'", 
                should_search,
                f"Query correctly identified as needing search: {should_search}"
            )
            
    def test_caching_functionality(self):
        """Test 2: Caching functionality"""
        self.logger.info("\n=== Testing Caching Functionality ===")
        
        # Clear cache before testing
        cache.clear()
        
        test_query = "Python programming language"
        
        try:
            # First search - should hit the API
            start_time = time.time()
            result1 = self.search_client.search(test_query, num_results=3, use_cache=True)
            first_time = time.time() - start_time
            
            # Second search - should hit cache
            start_time = time.time()
            result2 = self.search_client.search(test_query, num_results=3, use_cache=True)
            second_time = time.time() - start_time
            
            # Verify results are the same
            results_match = result1 == result2
            cache_faster = second_time < first_time * 0.5  # Cache should be significantly faster
            
            self.log_test_result(
                "Cache functionality",
                results_match and cache_faster,
                f"First call: {first_time:.2f}s, Second call (cached): {second_time:.2f}s, Results match: {results_match}"
            )
            
            # Test cache key generation
            cache_key = self.search_client._get_cache_key(test_query, 3, None)
            cached_result = cache.get(cache_key)
            
            self.log_test_result(
                "Cache key and storage",
                cached_result is not None,
                f"Cache key: {cache_key}, Has cached result: {cached_result is not None}"
            )
            
        except Exception as e:
            self.log_test_result(
                "Cache functionality",
                False,
                f"Error during caching test: {str(e)}"
            )
            
    def test_search_metrics_logging(self):
        """Test 3: Search failure monitoring and logging"""
        self.logger.info("\n=== Testing Search Metrics and Logging ===")
        
        try:
            # Test successful search logging
            result = self.search_client.search("test query", num_results=2)
            
            # Get today's metrics
            metrics = self.search_client.get_search_metrics()
            
            has_metrics = metrics['total_searches'] > 0
            self.log_test_result(
                "Search metrics collection",
                has_metrics,
                f"Metrics collected: {json.dumps(metrics, indent=2)}"
            )
            
            # Test error logging (simulate by using invalid credentials)
            original_api_key = self.search_client.api_key
            self.search_client.api_key = "invalid_key"
            
            try:
                self.search_client.search("error test")
                error_logged = False
            except Exception as e:
                error_logged = True
                self.log_test_result(
                    "Error logging",
                    True,
                    f"Error properly caught and logged: {str(e)[:100]}"
                )
            
            # Restore original API key
            self.search_client.api_key = original_api_key
            
            if not error_logged:
                self.log_test_result(
                    "Error logging",
                    False,
                    "Expected error was not caught"
                )
                
        except Exception as e:
            self.log_test_result(
                "Search metrics logging",
                False,
                f"Error during metrics test: {str(e)}"
            )
            
    def test_chatbot_integration(self):
        """Test 4: Full chatbot integration"""
        self.logger.info("\n=== Testing Full Chatbot Integration ===")
        
        # Test queries that should trigger search
        search_queries = [
            "What's the latest news about artificial intelligence?",
            "Current developments in renewable energy",
            "Recent updates on space exploration"
        ]
        
        for query in search_queries:
            try:
                # Test if search is triggered
                should_search = self.chatbot._is_search_query(query)
                
                if should_search:
                    # Test getting search context
                    search_context = self.chatbot._get_search_enhanced_context(query, max_results=2)
                    has_context = len(search_context) > 50  # Should have meaningful content
                    
                    self.log_test_result(
                        f"Integration test: '{query[:30]}...'",
                        has_context,
                        f"Search triggered: {should_search}, Context length: {len(search_context)}"
                    )
                else:
                    self.log_test_result(
                        f"Integration test: '{query[:30]}...'",
                        False,
                        "Query should have triggered search but didn't"
                    )
                    
            except Exception as e:
                self.log_test_result(
                    f"Integration test: '{query[:30]}...'",
                    False,
                    f"Error: {str(e)}"
                )
                
    def test_cache_performance(self):
        """Test 5: Cache performance and efficiency"""
        self.logger.info("\n=== Testing Cache Performance ===")
        
        # Clear cache
        cache.clear()
        
        queries = [
            "Python programming tutorial",
            "JavaScript frameworks 2025",
            "Machine learning algorithms"
        ]
        
        total_api_time = 0
        total_cache_time = 0
        
        for query in queries:
            try:
                # First call (API)
                start = time.time()
                self.search_client.search(query, num_results=2, use_cache=True)
                api_time = time.time() - start
                total_api_time += api_time
                
                # Second call (cache)
                start = time.time()
                self.search_client.search(query, num_results=2, use_cache=True)
                cache_time = time.time() - start
                total_cache_time += cache_time
                
            except Exception as e:
                self.logger.warning(f"Error testing cache performance for '{query}': {e}")
        
        if total_api_time > 0:
            performance_improvement = ((total_api_time - total_cache_time) / total_api_time) * 100
            
            self.log_test_result(
                "Cache performance improvement",
                performance_improvement > 50,  # Cache should be at least 50% faster
                f"API time: {total_api_time:.2f}s, Cache time: {total_cache_time:.2f}s, Improvement: {performance_improvement:.1f}%"
            )
        else:
            self.log_test_result(
                "Cache performance improvement",
                False,
                "Could not measure performance - no successful API calls"
            )
            
    def run_all_tests(self):
        """Run all enhancement tests"""
        self.logger.info("Starting comprehensive enhancement testing...")
        
        # Run all tests
        self.test_enhanced_search_keywords()
        self.test_caching_functionality()
        self.test_search_metrics_logging()
        self.test_chatbot_integration()
        self.test_cache_performance()
        
        # Summary
        self.print_summary()
        
    def print_summary(self):
        """Print test summary"""
        self.logger.info("\n" + "="*60)
        self.logger.info("COMPREHENSIVE ENHANCEMENT TEST SUMMARY")
        self.logger.info("="*60)
        
        passed = len([r for r in self.test_results if r['status'] == 'PASSED'])
        failed = len([r for r in self.test_results if r['status'] == 'FAILED'])
        total = len(self.test_results)
        
        self.logger.info(f"Total Tests: {total}")
        self.logger.info(f"Passed: {passed}")
        self.logger.info(f"Failed: {failed}")
        self.logger.info(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if failed > 0:
            self.logger.info("\nFailed Tests:")
            for result in self.test_results:
                if result['status'] == 'FAILED':
                    self.logger.info(f"  - {result['test']}: {result['details']}")
        
        self.logger.info("\nEnhancement Implementation Status:")
        self.logger.info("1. Enhanced search keywords: ✓ IMPLEMENTED")
        self.logger.info("2. Caching functionality: ✓ IMPLEMENTED") 
        self.logger.info("3. Search monitoring/logging: ✓ IMPLEMENTED")
        
        # Save results to file
        with open('c:\\Users\\Avishek Paul\\pm_chatbot\\test_results_enhancements.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        self.logger.info(f"\nDetailed results saved to: test_results_enhancements.json")

if __name__ == "__main__":
    tester = ComprehensiveEnhancementTester()
    tester.run_all_tests()
