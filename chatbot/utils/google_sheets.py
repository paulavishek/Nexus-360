import os
import json
import gspread
import time
from oauth2client.service_account import ServiceAccountCredentials
from django.conf import settings
from django.core.cache import cache

class GoogleSheetsClient:
    """
    Client for interacting with Google Sheets API as a database
    """
    def __init__(self, sheet_id=None):
        # Scope for Google Sheets API
        self.scope = ['https://spreadsheets.google.com/feeds',
                     'https://www.googleapis.com/auth/drive']
        
        # Get the credentials file path from settings
        self.credentials_file = settings.GOOGLE_SHEETS_CREDENTIALS_FILE
        
        # If a specific sheet ID is provided, use it; otherwise, use default from settings
        self.sheet_id = sheet_id if sheet_id else settings.GOOGLE_SHEETS_PROJECT_DB
        
        # Store all available sheet IDs for multi-sheet querying
        self.available_sheets = self._load_available_sheets()
        
        self.client = None

        # Set last update time for cache invalidation
        self.last_update_time = {}
    
    def _load_available_sheets(self):
        """Load all available sheet IDs from settings"""
        sheets = {}
        
        # Load the primary sheet
        if hasattr(settings, 'GOOGLE_SHEETS_PROJECT_DB'):
            sheets['default'] = settings.GOOGLE_SHEETS_PROJECT_DB
        
        # Load additional sheets from settings
        if hasattr(settings, 'ADDITIONAL_GOOGLE_SHEETS'):
            for name, sheet_id in settings.ADDITIONAL_GOOGLE_SHEETS.items():
                sheets[name] = sheet_id
                
        return sheets
    
    def connect(self):
        """Connect to Google Sheets API with improved error handling"""
        try:
            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                self.credentials_file, self.scope)
            self.client = gspread.authorize(credentials)
            return True
        except FileNotFoundError:
            print(f"Error: Credentials file not found at {self.credentials_file}")
            return False
        except ValueError as e:
            print(f"Error: Invalid credentials format - {e}")
            return False
        except Exception as e:
            print(f"Error connecting to Google Sheets API: {e}")
            return False
            
    def get_all_data(self, use_cache=True):
        """
        Get all data from all sheets to provide context for the chatbot
        
        Args:
            use_cache (bool): Whether to use cached data if available
            
        Returns:
            dict: All available data from the database
        """
        # Create cache key for all data
        cache_key = "all_database_data"
        
        # Try to get data from cache if use_cache is True
        if use_cache:
            cached_data = cache.get(cache_key)
            if cached_data:
                return cached_data
                
        # If not in cache or cache not to be used, fetch from all sheets
        if not self.client:
            if not self.connect():
                return {"error": "Could not connect to database"}
                
        try:
            all_data = {}
            
            # Get data from each available sheet
            for sheet_name, sheet_id in self.available_sheets.items():
                sheet_data = self._get_sheet_data(sheet_id, sheet_name)
                all_data[sheet_name] = sheet_data
                
            # Cache the combined results
            if use_cache:
                cache.set(cache_key, all_data, settings.GOOGLE_SHEETS_CACHE_TIMEOUT)
                
            return all_data
            
        except Exception as e:
            print(f"Error fetching all database data: {e}")
            return {"error": str(e)}
            
    def _get_sheet_data(self, sheet_id, sheet_name):
        """
        Get all data from a specific Google Sheet
        
        Args:
            sheet_id (str): ID of the Google Sheet
            sheet_name (str): Name identifier for the sheet
            
        Returns:
            dict: All worksheet data from this sheet
        """
        try:
            spreadsheet = self.client.open_by_key(sheet_id)
            worksheets = spreadsheet.worksheets()
            
            sheet_data = {}
            
            for worksheet in worksheets:
                try:
                    # Get all records from this worksheet
                    worksheet_data = worksheet.get_all_records()
                    
                    # Add source information to each record
                    for record in worksheet_data:
                        record['_source_sheet'] = sheet_name
                        record['_source_worksheet'] = worksheet.title
                    
                    sheet_data[worksheet.title] = worksheet_data
                except Exception as worksheet_error:
                    print(f"Error fetching data from worksheet {worksheet.title}: {worksheet_error}")
                    sheet_data[worksheet.title] = {"error": str(worksheet_error)}
                    
            return sheet_data
            
        except Exception as e:
            print(f"Error fetching data from sheet {sheet_name}: {e}")
            return {"error": str(e)}
            
    def get_available_sheet_names(self):
        """Get a list of all available sheet names"""
        return list(self.available_sheets.keys())

    def clear_cache(self):
        """Clear all cached database data"""
        cache.delete("all_database_data")
        self.last_update_time = {}