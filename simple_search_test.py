import os
os.environ['DB_TYPE'] = 'sqlite'
os.environ['DJANGO_SETTINGS_MODULE'] = 'project_chatbot.settings'
import django
django.setup()

from chatbot.utils.google_search import GoogleSearchClient

print("=== GOOGLE SEARCH RECENCY TEST ===")

client = GoogleSearchClient()

# Test with queries that should return recent information
test_queries = [
    "current events May 2025",
    "latest news 2025", 
    "recent AI developments 2025",
    "May 27 2025 news"
]

for query in test_queries:
    print(f"\nQuery: '{query}'")
    print("-" * 50)
    
    try:
        results = client.search(query, num_results=3)
        print(f"Found {len(results)} results")
        
        recent_count = 0
        for i, result in enumerate(results):
            title = result.get('title', '')
            snippet = result.get('snippet', '')
            
            # Check for 2025 or recent indicators
            content = (title + ' ' + snippet).lower()
            has_2025 = '2025' in content
            has_recent = any(term in content for term in ['recent', 'latest', 'current', 'today', 'this week', 'may'])
            
            if has_2025 or has_recent:
                recent_count += 1
                
            print(f"  {i+1}. {title[:60]}...")
            print(f"     Has 2025: {has_2025}, Has recent terms: {has_recent}")
            print(f"     URL: {result.get('link', '')}")
            
        print(f"\nRecent information score: {recent_count}/{len(results)} results")
        
    except Exception as e:
        print(f"Error: {e}")

print("\n" + "="*60)
print("CONCLUSION: Google Search Integration Assessment")
print("="*60)
