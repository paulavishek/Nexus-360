"""
Test script to verify Google Sheets connection and data retrieval
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_chatbot.settings')
django.setup()

from chatbot.utils.google_sheets import GoogleSheetsClient
from chatbot.utils.chatbot_service import ChatbotService
from django.conf import settings
import json

def test_google_sheets_connection():
    """Test Google Sheets connection and data retrieval"""
    
    print("=" * 70)
    print("GOOGLE SHEETS CONNECTION TEST")
    print("=" * 70)
    
    # Check settings
    print("\n1. Checking Configuration...")
    print(f"   USE_SQL_DATABASE: {getattr(settings, 'USE_SQL_DATABASE', 'Not set')}")
    print(f"   GOOGLE_SHEETS_CREDENTIALS_FILE: {getattr(settings, 'GOOGLE_SHEETS_CREDENTIALS_FILE', 'Not set')}")
    print(f"   GOOGLE_SHEETS_PROJECT_DB: {getattr(settings, 'GOOGLE_SHEETS_PROJECT_DB', 'Not set')}")
    
    # Check if credentials file exists
    creds_file = getattr(settings, 'GOOGLE_SHEETS_CREDENTIALS_FILE', '')
    if os.path.exists(creds_file):
        print(f"   ✓ Credentials file exists: {creds_file}")
    else:
        print(f"   ✗ Credentials file NOT found: {creds_file}")
        return
    
    # Test connection
    print("\n2. Testing Google Sheets Connection...")
    try:
        sheets_client = GoogleSheetsClient()
        connected = sheets_client.connect()
        
        if connected:
            print("   ✓ Successfully connected to Google Sheets API")
        else:
            print("   ✗ Failed to connect to Google Sheets API")
            return
    except Exception as e:
        print(f"   ✗ Connection error: {e}")
        return
    
    # Get available sheets
    print("\n3. Available Sheets:")
    sheet_names = sheets_client.get_available_sheet_names()
    for name in sheet_names:
        print(f"   - {name}")
    
    # Test data retrieval
    print("\n4. Testing Data Retrieval...")
    try:
        data = sheets_client.get_all_data(use_cache=False)
        
        if data and 'error' not in data:
            print("   ✓ Successfully retrieved data from Google Sheets")
            
            # Display summary
            print("\n5. Data Summary:")
            for sheet_name, sheet_data in data.items():
                print(f"\n   Sheet: {sheet_name}")
                if isinstance(sheet_data, dict):
                    for worksheet_name, worksheet_data in sheet_data.items():
                        if isinstance(worksheet_data, list):
                            print(f"      Worksheet: {worksheet_name}")
                            print(f"         Rows: {len(worksheet_data)}")
                            if len(worksheet_data) > 0 and isinstance(worksheet_data[0], dict):
                                print(f"         Columns: {', '.join(worksheet_data[0].keys())}")
                        elif isinstance(worksheet_data, dict) and 'error' in worksheet_data:
                            print(f"      Worksheet: {worksheet_name} - Error: {worksheet_data['error']}")
        else:
            print(f"   ✗ Error retrieving data: {data.get('error', 'Unknown error')}")
            return
            
    except Exception as e:
        print(f"   ✗ Data retrieval error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test chatbot service integration
    print("\n6. Testing Chatbot Service Integration...")
    try:
        chatbot = ChatbotService()
        db_data = chatbot.get_database_data(use_cache=False)
        
        if db_data and 'error' not in db_data:
            print("   ✓ Chatbot service successfully integrated with Google Sheets")
        else:
            print(f"   ✗ Chatbot service error: {db_data.get('error', 'Unknown error') if db_data else 'No data returned'}")
    except Exception as e:
        print(f"   ✗ Chatbot service error: {e}")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    print("\nNext Steps:")
    print("1. Ensure your Google Sheet is shared with the service account email:")
    print("   pm-chatbot-gemini@gen-lang-client-0656398844.iam.gserviceaccount.com")
    print("2. Verify the Google Sheet ID in your .env file is correct")
    print("3. Restart your Django server if you made any configuration changes")
    print("=" * 70)

if __name__ == "__main__":
    test_google_sheets_connection()
