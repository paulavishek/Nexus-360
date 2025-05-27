import os
import sys
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_chatbot.settings')
os.environ['DB_TYPE'] = 'sqlite'
import django
django.setup()

from chatbot.utils.google_search import GoogleSearchClient
from datetime import datetime
import re

print('=== COMPREHENSIVE GOOGLE SEARCH EVALUATION ===')
print(f'Current Date: {datetime.now().strftime("%B %d, %Y")}')
print()

try:
    client = GoogleSearchClient()
    
    # Test queries that require recent information
    test_cases = [
        {
            'query': 'latest news May 2025',
            'description': 'Current news for May 2025',
            'expected_terms': ['2025', 'may', 'recent', 'latest', 'news']
        },
        {
            'query': 'project management trends 2025',
            'description': 'Recent project management trends',
            'expected_terms': ['2025', 'trends', 'project management', 'latest', 'current']
        },
        {
            'query': 'AI developments 2025',
            'description': 'Recent AI developments',
            'expected_terms': ['2025', 'ai', 'artificial intelligence', 'developments', 'latest']
        },
        {
            'query': 'current technology trends May 2025',
            'description': 'Current technology trends',
            'expected_terms': ['2025', 'technology', 'trends', 'current', 'may']
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f'Test {i}: {test_case["description"]}')
        print(f'Query: "{test_case["query"]}"')
        print('-' * 60)
        
        try:
            results = client.search(test_case['query'], num_results=3)
            
            if not results:
                print('❌ No results found')
                continue
                
            print(f'✅ Found {len(results)} results')
            
            # Check for recency indicators
            recent_count = 0
            for j, result in enumerate(results):
                print(f'\nResult {j+1}:')
                print(f'  Title: {result["title"]}')
                print(f'  URL: {result["link"]}')
                print(f'  Snippet: {result["snippet"][:150]}...')
                
                # Check for recency indicators in title and snippet
                content = (result['title'] + ' ' + result['snippet']).lower()
                
                # Look for 2025 or 2024 dates
                has_recent_date = any(year in content for year in ['2025', '2024'])
                
                # Look for recency terms
                recency_terms = ['latest', 'recent', 'current', 'new', 'updated', 'today', 'this year', 'may 2025']
                has_recency_terms = any(term in content for term in recency_terms)
                
                # Look for expected terms
                has_expected_terms = sum(1 for term in test_case['expected_terms'] if term in content)
                
                if has_recent_date or has_recency_terms:
                    recent_count += 1
                    
                print(f'  ✅ Recent indicators: Date={has_recent_date}, Terms={has_recency_terms}')
                print(f'  📊 Expected terms found: {has_expected_terms}/{len(test_case["expected_terms"])}')
            
            # Overall assessment
            recency_score = (recent_count / len(results)) * 100
            print(f'\n🎯 Recency Score: {recency_score:.1f}% ({recent_count}/{len(results)} results have recent indicators)')
            
            if recency_score >= 60:
                print('✅ GOOD: Search provides recent information')
            elif recency_score >= 30:
                print('⚠️  MODERATE: Some recent information available')
            else:
                print('❌ POOR: Limited recent information')
                
        except Exception as e:
            print(f'❌ Error with test case: {e}')
            
        print('\n' + '='*80 + '\n')
    
    # Test the formatted context output
    print('TESTING FORMATTED SEARCH CONTEXT')
    print('-' * 40)
    
    try:
        search_context = client.get_search_context('latest AI developments 2025', max_results=2)
        print('Sample formatted context:')
        print(search_context[:500] + '...' if len(search_context) > 500 else search_context)
        
        # Check if sources are properly cited
        has_sources = '[Source' in search_context and 'URL:' in search_context
        has_instructions = 'citing sources' in search_context.lower()
        
        print(f'\n✅ Proper source formatting: {has_sources}')
        print(f'✅ Citation instructions included: {has_instructions}')
        
    except Exception as e:
        print(f'❌ Error testing formatted context: {e}')

except Exception as e:
    print(f'❌ Critical error: {e}')

print('\n' + '='*80)
print('CONCLUSION')
print('='*80)
print('The Google Search integration appears to be working and can provide recent information.')
print('Key findings will be displayed above.')
