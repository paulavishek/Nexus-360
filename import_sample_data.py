#!/usr/bin/env python
"""
Utility script to import sample data into Google Sheets.
This script uses the sample_data.json file and uploads it to Google Sheets.
"""

import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def import_sample_data():
    """Import sample data from JSON file to Google Sheets"""
    
    # Get environment variables
    creds_file = os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE')
    sheet_id = os.getenv('GOOGLE_SHEETS_PROJECT_DB')
    
    if not creds_file or not sheet_id:
        print("Error: Missing environment variables.")
        print("Please make sure GOOGLE_SHEETS_CREDENTIALS_FILE and GOOGLE_SHEETS_PROJECT_DB are set in your .env file.")
        return False
    
    try:
        # Load sample data
        with open('sample_data.json', 'r') as file:
            sample_data = json.load(file)
        
        # Connect to Google Sheets
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
        gc = gspread.authorize(credentials)
        
        # Open the spreadsheet by ID
        spreadsheet = gc.open_by_key(sheet_id)
        
        # Import Projects data
        try:
            # Check if Projects worksheet exists, if not create it
            try:
                projects_sheet = spreadsheet.worksheet("Projects")
                # Clear existing data if sheet exists
                projects_sheet.clear()
            except gspread.exceptions.WorksheetNotFound:
                projects_sheet = spreadsheet.add_worksheet(title="Projects", rows=100, cols=20)
            
            # Prepare headers and data
            projects_data = sample_data.get("Projects", [])
            if not projects_data:
                print("No projects data found in sample_data.json")
                return False
            
            # Get headers from the first project
            headers = list(projects_data[0].keys())
            
            # Prepare rows to upload
            rows = [headers]
            for project in projects_data:
                rows.append([project.get(header, "") for header in headers])
            
            # Update the worksheet
            projects_sheet.update(rows)
            print(f"Successfully imported {len(projects_data)} projects")
            
        except Exception as e:
            print(f"Error importing projects data: {e}")
            return False
        
        # Import Members data
        try:
            # Check if Members worksheet exists, if not create it
            try:
                members_sheet = spreadsheet.worksheet("Members")
                # Clear existing data if sheet exists
                members_sheet.clear()
            except gspread.exceptions.WorksheetNotFound:
                members_sheet = spreadsheet.add_worksheet(title="Members", rows=100, cols=20)
            
            # Prepare headers and data
            members_data = sample_data.get("Members", [])
            if not members_data:
                print("No members data found in sample_data.json")
                return False
            
            # Get headers from the first member
            headers = list(members_data[0].keys())
            
            # Prepare rows to upload
            rows = [headers]
            for member in members_data:
                rows.append([member.get(header, "") for header in headers])
            
            # Update the worksheet
            members_sheet.update(rows)
            print(f"Successfully imported {len(members_data)} members")
            
        except Exception as e:
            print(f"Error importing members data: {e}")
            return False
        
        print("\nSample data has been successfully imported to Google Sheets!")
        print(f"Spreadsheet ID: {sheet_id}")
        return True
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

if __name__ == "__main__":
    print("Starting import of sample data to Google Sheets...")
    import_sample_data()