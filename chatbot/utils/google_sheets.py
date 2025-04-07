import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from django.conf import settings

class GoogleSheetsClient:
    """
    Client for interacting with Google Sheets API
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
    
    def get_all_projects(self, sheet_name=None):
        """
        Get all projects from the Google Sheet with improved error handling
        
        Args:
            sheet_name (str, optional): Name of the sheet to query. Defaults to None (uses default sheet).
        """
        if not self.client:
            if not self.connect():
                return []
        
        try:
            # If sheet_name is provided and exists in available_sheets, use that sheet ID
            if sheet_name and sheet_name in self.available_sheets:
                current_sheet_id = self.available_sheets[sheet_name]
            else:
                current_sheet_id = self.sheet_id
            
            try:
                spreadsheet = self.client.open_by_key(current_sheet_id)
            except gspread.exceptions.APIError as e:
                print(f"API Error accessing spreadsheet: {e}")
                if "404" in str(e):
                    print(f"Spreadsheet with ID {current_sheet_id} not found. Check if the ID is correct.")
                elif "403" in str(e):
                    print(f"Permission denied for spreadsheet {current_sheet_id}. Check if the service account has access.")
                return []
            
            try:
                sheet = spreadsheet.worksheet("Projects")
            except gspread.exceptions.WorksheetNotFound:
                print(f"'Projects' worksheet not found in spreadsheet {current_sheet_id}")
                return []
            
            projects = sheet.get_all_records()
            
            # Add source information to each project
            for project in projects:
                project['_source_sheet'] = sheet_name or 'default'
            
            return projects
        except gspread.exceptions.APIError as e:
            print(f"Google Sheets API Error: {e}")
            # Handle rate limiting
            if "429" in str(e):
                print("Rate limit exceeded. Waiting before retrying...")
                import time
                time.sleep(5)  # Wait 5 seconds before the caller might retry
            return []
        except Exception as e:
            print(f"Error fetching projects: {e}")
            return []

    def validate_sheet_structure(self, sheet_name=None):
        """
        Validates that the spreadsheet has the expected structure
        
        Args:
            sheet_name (str, optional): Name of the sheet to validate
            
        Returns:
            dict: Validation results with issues found
        """
        if not self.client:
            if not self.connect():
                return {"valid": False, "errors": ["Could not connect to Google Sheets"]}
        
        try:
            # Determine which sheet to use
            if sheet_name and sheet_name in self.available_sheets:
                current_sheet_id = self.available_sheets[sheet_name]
            else:
                current_sheet_id = self.sheet_id
            
            spreadsheet = self.client.open_by_key(current_sheet_id)
            
            # Check for required worksheets
            worksheet_names = [ws.title for ws in spreadsheet.worksheets()]
            errors = []
            
            if "Projects" not in worksheet_names:
                errors.append("Missing 'Projects' worksheet")
            if "Members" not in worksheet_names:
                errors.append("Missing 'Members' worksheet")
            
            # Check for required columns in Projects
            if "Projects" in worksheet_names:
                projects_sheet = spreadsheet.worksheet("Projects")
                headers = projects_sheet.row_values(1)
                required_project_fields = ["name", "description", "start_date", "end_date", "budget", "expenses", "status"]
                
                for field in required_project_fields:
                    if field.lower() not in [h.lower() for h in headers]:
                        errors.append(f"Missing '{field}' column in Projects worksheet")
            
            # Check for required columns in Members
            if "Members" in worksheet_names:
                members_sheet = spreadsheet.worksheet("Members")
                headers = members_sheet.row_values(1)
                required_member_fields = ["project_name", "name", "role", "email"]
                
                for field in required_member_fields:
                    if field.lower() not in [h.lower() for h in headers]:
                        errors.append(f"Missing '{field}' column in Members worksheet")
            
            return {
                "valid": len(errors) == 0,
                "sheet_name": sheet_name or "default",
                "sheets_found": worksheet_names,
                "errors": errors
            }
            
        except Exception as e:
            return {
                "valid": False,
                "sheet_name": sheet_name or "default",
                "errors": [f"Error validating sheet structure: {str(e)}"]
            }
    
    def get_all_projects_from_all_sheets(self):
        """Get all projects from all configured Google Sheets"""
        all_projects = []
        
        # Loop through all available sheets
        for name, sheet_id in self.available_sheets.items():
            # Temporarily set the sheet ID
            self.sheet_id = sheet_id
            
            # Get projects from this sheet
            sheet_projects = self.get_all_projects(name)
            all_projects.extend(sheet_projects)
        
        # Reset to default sheet
        self.sheet_id = self.available_sheets.get('default', self.sheet_id)
        
        return all_projects
    
    def get_project_by_name(self, name, sheet_name=None):
        """
        Get a specific project by name
        
        Args:
            name (str): Project name to search for
            sheet_name (str, optional): Name of the sheet to search in. If None, searches all sheets.
        """
        if sheet_name:
            projects = self.get_all_projects(sheet_name)
            for project in projects:
                if project.get('name', '').lower() == name.lower():
                    return project
        else:
            # Search across all sheets
            projects = self.get_all_projects_from_all_sheets()
            for project in projects:
                if project.get('name', '').lower() == name.lower():
                    return project
        
        return None
    
    def get_project_members(self, project_name=None, project_id=None, sheet_name=None):
        """
        Get members for a specific project or all members
        
        Args:
            project_name (str, optional): Project name to filter members by
            project_id (str, optional): Project ID to filter members by
            sheet_name (str, optional): Name of the sheet to query. If None, uses default sheet.
        """
        if not self.client:
            if not self.connect():
                return []
        
        try:
            # Determine which sheet to use
            if sheet_name and sheet_name in self.available_sheets:
                current_sheet_id = self.available_sheets[sheet_name]
            else:
                current_sheet_id = self.sheet_id
            
            sheet = self.client.open_by_key(current_sheet_id).worksheet("Members")
            all_members = sheet.get_all_records()
            
            # Add source information
            for member in all_members:
                member['_source_sheet'] = sheet_name or 'default'
            
            if project_name:
                return [m for m in all_members if m.get('project_name', '').lower() == project_name.lower()]
            elif project_id:
                return [m for m in all_members if str(m.get('project_id', '')) == str(project_id)]
            else:
                return all_members
        except Exception as e:
            print(f"Error fetching project members: {e}")
            return []
    
    def get_all_members_from_all_sheets(self):
        """Get all members from all configured Google Sheets"""
        all_members = []
        
        # Loop through all available sheets
        for name, sheet_id in self.available_sheets.items():
            # Temporarily set the sheet ID
            self.sheet_id = sheet_id
            
            # Get members from this sheet
            sheet_members = self.get_project_members(sheet_name=name)
            all_members.extend(sheet_members)
        
        # Reset to default sheet
        self.sheet_id = self.available_sheets.get('default', self.sheet_id)
        
        return all_members
    
    def get_budget_statistics(self, sheet_name=None):
        """
        Get budget statistics for all projects in a sheet or all sheets
        
        Args:
            sheet_name (str, optional): Name of the sheet to analyze. If None, analyzes all sheets.
        """
        if sheet_name:
            projects = self.get_all_projects(sheet_name)
        else:
            projects = self.get_all_projects_from_all_sheets()
            
        over_budget = [p for p in projects if float(p.get('expenses', 0)) > float(p.get('budget', 0))]
        under_budget = [p for p in projects if float(p.get('expenses', 0)) <= float(p.get('budget', 0))]
        
        return {
            'total_projects': len(projects),
            'over_budget_count': len(over_budget),
            'under_budget_count': len(under_budget),
            'over_budget_projects': over_budget,
            'under_budget_projects': under_budget,
            'sheets_analyzed': [sheet_name] if sheet_name else list(self.available_sheets.keys())
        }
    
    def get_project_count_by_status(self, sheet_name=None):
        """
        Get counts of projects by status
        
        Args:
            sheet_name (str, optional): Name of the sheet to analyze. If None, analyzes all sheets.
        """
        if sheet_name:
            projects = self.get_all_projects(sheet_name)
        else:
            projects = self.get_all_projects_from_all_sheets()
            
        status_counts = {}
        
        for project in projects:
            status = project.get('status', 'unknown')
            if status in status_counts:
                status_counts[status] += 1
            else:
                status_counts[status] = 1
        
        return status_counts
    
    def get_available_sheet_names(self):
        """Get a list of all available sheet names"""
        return list(self.available_sheets.keys())