"""
Test script to verify Gemini API key is working correctly
"""
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'project_chatbot.settings'

import django
django.setup()

from chatbot.utils.gemini_client import GeminiClient

def test_gemini():
    print("Testing Gemini API key...")
    print("-" * 50)
    
    try:
        # Initialize the client
        print("1. Initializing Gemini client...")
        client = GeminiClient()
        print("   ✅ Client initialized successfully")
        print(f"   API Key: {client.api_key[:20]}...{client.api_key[-10:]}")
        
        # Test a simple query
        print("\n2. Testing simple query...")
        response = client.get_chatbot_response(
            prompt="Say 'Hello, the API is working!'",
            database_data=None,
            history=None,
            context=None
        )
        print(f"   ✅ Response received: {response}")
        
        # Test with history
        print("\n3. Testing with conversation history...")
        history = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello! How can I help you?"}
        ]
        response2 = client.get_chatbot_response(
            prompt="What's 2+2?",
            database_data=None,
            history=history,
            context=None
        )
        print(f"   ✅ Response with history: {response2}")
        
        print("\n" + "=" * 50)
        print("✅ ALL TESTS PASSED! Gemini API is working correctly.")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Verify the API key in your .env file is correct")
        print("2. Check that the Generative Language API is enabled at:")
        print("   https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com")
        print("3. Ensure your API key has the correct permissions")
        return False
    
    return True

if __name__ == "__main__":
    test_gemini()
