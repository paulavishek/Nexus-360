"""
Comprehensive Integration Check for Nexus360
This script tests all API connections and integrations to ensure they're working properly.
"""

import os
import sys
import json
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_chatbot.settings')
import django
django.setup()

from django.conf import settings
from colorama import init, Fore, Style
import time

# Initialize colorama for colored terminal output
init(autoreset=True)

class IntegrationChecker:
    """Check all integrations and API connections"""
    
    def __init__(self):
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': []
        }
    
    def print_header(self, text):
        """Print a formatted header"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}{text.center(70)}")
        print(f"{Fore.CYAN}{'='*70}\n")
    
    def print_section(self, text):
        """Print a formatted section header"""
        print(f"\n{Fore.YELLOW}{'─'*70}")
        print(f"{Fore.YELLOW}[{text}]")
        print(f"{Fore.YELLOW}{'─'*70}")
    
    def print_success(self, text):
        """Print success message"""
        print(f"{Fore.GREEN}✓ {text}")
        self.results['passed'].append(text)
    
    def print_failure(self, text):
        """Print failure message"""
        print(f"{Fore.RED}✗ {text}")
        self.results['failed'].append(text)
    
    def print_warning(self, text):
        """Print warning message"""
        print(f"{Fore.YELLOW}⚠ {text}")
        self.results['warnings'].append(text)
    
    def print_info(self, text):
        """Print info message"""
        print(f"{Fore.WHITE}  {text}")
    
    def check_env_file(self):
        """Check if .env file exists and has required variables"""
        self.print_section("Environment Configuration Check")
        
        env_path = BASE_DIR / '.env'
        if not env_path.exists():
            self.print_failure(".env file not found!")
            return False
        
        self.print_success(".env file found")
        
        # Required environment variables
        required_vars = {
            'DJANGO_SECRET_KEY': 'Django secret key',
            'OPENAI_API_KEY': 'OpenAI API key',
            'GOOGLE_GEMINI_API_KEY': 'Google Gemini API key',
            'GOOGLE_SHEETS_CREDENTIALS_FILE': 'Google Sheets credentials file path',
            'GOOGLE_SHEETS_PROJECT_DB': 'Google Sheets database ID',
            'GOOGLE_SEARCH_API_KEY': 'Google Search API key',
            'GOOGLE_SEARCH_ENGINE_ID': 'Google Search Engine ID'
        }
        
        for var, description in required_vars.items():
            value = os.getenv(var)
            if value and value.strip():
                self.print_success(f"{description} is configured")
            else:
                self.print_failure(f"{description} is missing or empty")
        
        return True
    
    def check_google_sheets_credentials(self):
        """Check Google Sheets credentials file"""
        self.print_section("Google Sheets Credentials Check")
        
        creds_file = getattr(settings, 'GOOGLE_SHEETS_CREDENTIALS_FILE', None)
        if not creds_file:
            self.print_failure("GOOGLE_SHEETS_CREDENTIALS_FILE not configured")
            return False
        
        creds_path = Path(creds_file)
        if not creds_path.exists():
            self.print_failure(f"Credentials file not found at: {creds_file}")
            return False
        
        self.print_success("Credentials file exists")
        
        try:
            with open(creds_path, 'r') as f:
                creds_data = json.load(f)
                if 'client_email' in creds_data:
                    self.print_info(f"Service account: {creds_data['client_email']}")
                    self.print_success("Credentials file is valid JSON")
                else:
                    self.print_failure("Credentials file missing 'client_email'")
                    return False
        except json.JSONDecodeError:
            self.print_failure("Credentials file is not valid JSON")
            return False
        except Exception as e:
            self.print_failure(f"Error reading credentials: {str(e)}")
            return False
        
        return True
    
    def check_google_sheets_connection(self):
        """Test Google Sheets API connection"""
        self.print_section("Google Sheets API Connection Test")
        
        try:
            from chatbot.utils.google_sheets import GoogleSheetsClient
            
            client = GoogleSheetsClient()
            self.print_info("Attempting to connect to Google Sheets...")
            
            if client.connect():
                self.print_success("Successfully connected to Google Sheets API")
                
                # Try to fetch data
                self.print_info("Attempting to fetch data from spreadsheet...")
                data = client.get_all_data(use_cache=False)
                
                if 'error' in data:
                    self.print_failure(f"Error fetching data: {data['error']}")
                    return False
                
                # Count sheets and records
                total_sheets = len(data)
                total_records = sum(
                    len(worksheet_data) 
                    for sheet_data in data.values() 
                    if isinstance(sheet_data, dict)
                    for worksheet_data in sheet_data.values()
                    if isinstance(worksheet_data, list)
                )
                
                self.print_success(f"Successfully fetched data from {total_sheets} sheet(s)")
                self.print_info(f"Total records: {total_records}")
                
                # Display sheet structure
                for sheet_name, sheet_data in data.items():
                    if isinstance(sheet_data, dict):
                        self.print_info(f"  Sheet '{sheet_name}':")
                        for worksheet_name, worksheet_data in sheet_data.items():
                            if isinstance(worksheet_data, list):
                                self.print_info(f"    - {worksheet_name}: {len(worksheet_data)} records")
                
                return True
            else:
                self.print_failure("Failed to connect to Google Sheets API")
                return False
                
        except ImportError as e:
            self.print_failure(f"Import error: {str(e)}")
            return False
        except Exception as e:
            self.print_failure(f"Unexpected error: {str(e)}")
            return False
    
    def check_openai_api(self):
        """Test OpenAI API connection"""
        self.print_section("OpenAI API Connection Test")
        
        api_key = getattr(settings, 'OPENAI_API_KEY', None)
        if not api_key or not api_key.strip():
            self.print_failure("OpenAI API key not configured")
            return False
        
        self.print_success("OpenAI API key is configured")
        
        try:
            from chatbot.utils.openai_client import OpenAIClient
            
            client = OpenAIClient()
            self.print_info("Testing OpenAI API with a simple query...")
            
            test_prompt = "Say 'API test successful' if you can read this."
            response = client.get_chatbot_response(
                prompt=test_prompt,
                database_data=None,
                history=None,
                context=None
            )
            
            if response and "error" not in response.lower():
                self.print_success("OpenAI API is working correctly")
                self.print_info(f"Test response: {response[:100]}...")
                return True
            else:
                self.print_failure("OpenAI API returned an error or unexpected response")
                self.print_info(f"Response: {response}")
                return False
                
        except Exception as e:
            self.print_failure(f"Error testing OpenAI API: {str(e)}")
            self.print_warning("Note: This could be due to API quota limits or network issues")
            return False
    
    def check_gemini_api(self):
        """Test Google Gemini API connection"""
        self.print_section("Google Gemini API Connection Test")
        
        api_key = getattr(settings, 'GOOGLE_GEMINI_API_KEY', None)
        if not api_key or not api_key.strip():
            self.print_failure("Google Gemini API key not configured")
            return False
        
        self.print_success("Google Gemini API key is configured")
        
        try:
            from chatbot.utils.gemini_client import GeminiClient
            
            client = GeminiClient()
            self.print_info("Testing Gemini API with a simple query...")
            
            test_prompt = "Say 'API test successful' if you can read this."
            response = client.get_chatbot_response(
                prompt=test_prompt,
                database_data=None,
                history=None,
                context=None
            )
            
            if response and "error" not in response.lower():
                self.print_success("Gemini API is working correctly")
                self.print_info(f"Test response: {response[:100]}...")
                return True
            else:
                self.print_failure("Gemini API returned an error or unexpected response")
                self.print_info(f"Response: {response}")
                return False
                
        except Exception as e:
            self.print_failure(f"Error testing Gemini API: {str(e)}")
            return False
    
    def check_google_search_api(self):
        """Test Google Search API connection"""
        self.print_section("Google Search API Connection Test")
        
        api_key = getattr(settings, 'GOOGLE_SEARCH_API_KEY', None)
        engine_id = getattr(settings, 'GOOGLE_SEARCH_ENGINE_ID', None)
        enabled = getattr(settings, 'ENABLE_WEB_SEARCH', False)
        
        if not enabled:
            self.print_warning("Google Search is disabled in settings (ENABLE_WEB_SEARCH=False)")
            return True
        
        if not api_key or not api_key.strip():
            self.print_failure("Google Search API key not configured")
            return False
        
        if not engine_id or not engine_id.strip():
            self.print_failure("Google Search Engine ID not configured")
            return False
        
        self.print_success("Google Search API credentials are configured")
        
        try:
            from chatbot.utils.google_search import GoogleSearchClient
            
            client = GoogleSearchClient()
            self.print_info("Testing Google Search API with a simple query...")
            
            test_query = "Python programming"
            results = client.search(test_query, num_results=3, use_cache=False)
            
            if results and len(results) > 0:
                self.print_success(f"Google Search API is working correctly ({len(results)} results)")
                for i, result in enumerate(results[:3], 1):
                    self.print_info(f"  {i}. {result.get('title', 'No title')[:60]}...")
                return True
            elif results is not None and len(results) == 0:
                self.print_warning("Google Search API returned no results (this might be okay)")
                return True
            else:
                self.print_failure("Google Search API returned None or invalid response")
                return False
                
        except Exception as e:
            self.print_failure(f"Error testing Google Search API: {str(e)}")
            return False
    
    def check_database_connection(self):
        """Test database connection"""
        self.print_section("Database Connection Test")
        
        try:
            from django.db import connection
            
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
            
            db_engine = settings.DATABASES['default']['ENGINE']
            db_name = settings.DATABASES['default']['NAME']
            
            self.print_success("Database connection successful")
            self.print_info(f"Database engine: {db_engine}")
            self.print_info(f"Database name: {db_name}")
            
            # Check for migrations
            from django.db.migrations.executor import MigrationExecutor
            executor = MigrationExecutor(connection)
            plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
            
            if plan:
                self.print_warning(f"Unapplied migrations found: {len(plan)} migration(s)")
                self.print_info("Run 'python manage.py migrate' to apply them")
            else:
                self.print_success("All migrations are applied")
            
            return True
            
        except Exception as e:
            self.print_failure(f"Database connection error: {str(e)}")
            return False
    
    def check_django_channels(self):
        """Check Django Channels configuration"""
        self.print_section("Django Channels Configuration Test")
        
        try:
            asgi_app = getattr(settings, 'ASGI_APPLICATION', None)
            if not asgi_app:
                self.print_failure("ASGI_APPLICATION not configured")
                return False
            
            self.print_success(f"ASGI application configured: {asgi_app}")
            
            channel_layers = getattr(settings, 'CHANNEL_LAYERS', None)
            if not channel_layers:
                self.print_failure("CHANNEL_LAYERS not configured")
                return False
            
            backend = channel_layers.get('default', {}).get('BACKEND', 'Unknown')
            self.print_success(f"Channel layer backend: {backend}")
            
            if 'InMemoryChannelLayer' in backend:
                self.print_warning("Using InMemory channel layer (suitable for development only)")
            
            return True
            
        except Exception as e:
            self.print_failure(f"Error checking Django Channels: {str(e)}")
            return False
    
    def check_dependencies(self):
        """Check if all required Python packages are installed"""
        self.print_section("Python Dependencies Check")
        
        required_packages = {
            'django': 'Django',
            'channels': 'Django Channels',
            'openai': 'OpenAI',
            'google.generativeai': 'Google Generative AI',
            'gspread': 'gspread (Google Sheets)',
            'oauth2client': 'oauth2client',
            'requests': 'requests',
            'dotenv': 'python-dotenv'  # Package name is 'python-dotenv' but import is 'dotenv'
        }
        
        all_installed = True
        for package, name in required_packages.items():
            try:
                __import__(package)
                self.print_success(f"{name} is installed")
            except ImportError:
                self.print_failure(f"{name} is NOT installed")
                all_installed = False
        
        return all_installed
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("INTEGRATION CHECK SUMMARY")
        
        total_tests = len(self.results['passed']) + len(self.results['failed'])
        passed = len(self.results['passed'])
        failed = len(self.results['failed'])
        warnings = len(self.results['warnings'])
        
        print(f"\n{Fore.CYAN}Total Checks: {total_tests}")
        print(f"{Fore.GREEN}Passed: {passed}")
        print(f"{Fore.RED}Failed: {failed}")
        print(f"{Fore.YELLOW}Warnings: {warnings}\n")
        
        if failed == 0 and warnings == 0:
            print(f"{Fore.GREEN}{'🎉 ALL INTEGRATIONS ARE WORKING PERFECTLY! 🎉'.center(70)}\n")
        elif failed == 0:
            print(f"{Fore.YELLOW}{'✓ All critical integrations working (some warnings)'.center(70)}\n")
        else:
            print(f"{Fore.RED}{'✗ Some integrations need attention'.center(70)}\n")
            print(f"{Fore.RED}Failed checks:")
            for failure in self.results['failed']:
                print(f"{Fore.RED}  • {failure}")
            print()
        
        if warnings > 0:
            print(f"{Fore.YELLOW}Warnings:")
            for warning in self.results['warnings']:
                print(f"{Fore.YELLOW}  • {warning}")
            print()
    
    def run_all_checks(self):
        """Run all integration checks"""
        self.print_header("NEXUS360 INTEGRATION CHECKER")
        print(f"{Fore.WHITE}Checking all API connections and integrations...\n")
        
        # Run all checks
        self.check_env_file()
        self.check_dependencies()
        self.check_google_sheets_credentials()
        self.check_database_connection()
        self.check_django_channels()
        self.check_google_sheets_connection()
        self.check_gemini_api()
        self.check_openai_api()
        self.check_google_search_api()
        
        # Print summary
        self.print_summary()
        
        # Return exit code
        return 0 if len(self.results['failed']) == 0 else 1


def main():
    """Main function"""
    try:
        checker = IntegrationChecker()
        exit_code = checker.run_all_checks()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Check cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
