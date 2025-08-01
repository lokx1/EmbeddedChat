"""
Google Sheets API Service
Handles authentication and operations with Google Sheets
"""

import os
import json
from typing import List, Dict, Any, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

logger = logging.getLogger(__name__)

class GoogleSheetsService:
    """Google Sheets API service for reading and writing data"""
    
    # Scopes for read and write access
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive.file'
    ]
    
    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialize Google Sheets service
        
        Args:
            credentials_path: Path to service account JSON file or OAuth credentials
        """
        self.credentials_path = credentials_path or self._find_credentials_file()
        self.service = None
        self.creds = None
        
    def _find_credentials_file(self) -> Optional[str]:
        """Find credentials file in common locations"""
        possible_paths = [
            "credentials.json",
            "service_account.json", 
            "google_credentials.json",
            os.path.join(os.path.dirname(__file__), "credentials.json"),
            os.path.join(os.path.dirname(__file__), "service_account.json"),
            os.path.join(os.path.dirname(__file__), "..", "..", "credentials.json"),
            os.path.join(os.path.dirname(__file__), "..", "..", "service_account.json"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"Found credentials file: {path}")
                return path
        
        logger.warning("No credentials file found in common locations")
        return None
    
    def authenticate(self) -> bool:
        """
        Authenticate with Google Sheets API
        
        Returns:
            bool: True if authentication successful
        """
        try:
            if not self.credentials_path or not os.path.exists(self.credentials_path):
                logger.error(f"Credentials file not found: {self.credentials_path}")
                return False
            
            # Check if it's a service account file
            with open(self.credentials_path, 'r') as f:
                cred_data = json.load(f)
            
            if cred_data.get('type') == 'service_account':
                # Service account authentication
                logger.info("Using service account authentication")
                self.creds = ServiceAccountCredentials.from_service_account_file(
                    self.credentials_path, scopes=self.SCOPES
                )
            else:
                # OAuth2 flow (for user credentials)
                logger.info("Using OAuth2 authentication")
                self.creds = None
                
                # Check for existing token
                token_path = 'token.json'
                if os.path.exists(token_path):
                    self.creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
                
                # If no valid credentials, run OAuth flow
                if not self.creds or not self.creds.valid:
                    if self.creds and self.creds.expired and self.creds.refresh_token:
                        self.creds.refresh(Request())
                    else:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            self.credentials_path, self.SCOPES
                        )
                        self.creds = flow.run_local_server(port=0)
                    
                    # Save credentials for next run
                    with open(token_path, 'w') as token:
                        token.write(self.creds.to_json())
            
            # Build the service
            self.service = build('sheets', 'v4', credentials=self.creds)
            logger.info("Google Sheets API authentication successful")
            return True
            
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            return False
    
    def read_sheet(self, spreadsheet_id: str, range_name: str) -> Optional[List[List[str]]]:
        """
        Read data from a Google Sheet
        
        Args:
            spreadsheet_id: The ID of the spreadsheet
            range_name: The A1 notation range to read (e.g., 'Sheet1!A1:D10')
            
        Returns:
            List of rows, where each row is a list of cell values
        """
        try:
            if not self.service:
                if not self.authenticate():
                    return None
            
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            logger.info(f"Read {len(values)} rows from {range_name}")
            return values
            
        except HttpError as e:
            logger.error(f"Error reading sheet: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error reading sheet: {str(e)}")
            return None
    
    def write_sheet(self, spreadsheet_id: str, range_name: str, values: List[List[Any]], 
                   value_input_option: str = 'RAW') -> bool:
        """
        Write data to a Google Sheet
        
        Args:
            spreadsheet_id: The ID of the spreadsheet
            range_name: The A1 notation range to write (e.g., 'Sheet1!A1')
            values: 2D array of values to write
            value_input_option: How to interpret input ('RAW' or 'USER_ENTERED')
            
        Returns:
            bool: True if write successful
        """
        try:
            if not self.service:
                if not self.authenticate():
                    return False
            
            body = {
                'values': values
            }
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption=value_input_option,
                body=body
            ).execute()
            
            updated_cells = result.get('updatedCells', 0)
            logger.info(f"Updated {updated_cells} cells in {range_name}")
            return True
            
        except HttpError as e:
            logger.error(f"Error writing to sheet: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error writing to sheet: {str(e)}")
            return False
    
    def append_sheet(self, spreadsheet_id: str, range_name: str, values: List[List[Any]],
                    value_input_option: str = 'RAW') -> bool:
        """
        Append data to a Google Sheet
        
        Args:
            spreadsheet_id: The ID of the spreadsheet
            range_name: The A1 notation range (e.g., 'Sheet1!A1')
            values: 2D array of values to append
            value_input_option: How to interpret input ('RAW' or 'USER_ENTERED')
            
        Returns:
            bool: True if append successful
        """
        try:
            if not self.service:
                if not self.authenticate():
                    return False
            
            body = {
                'values': values
            }
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption=value_input_option,
                body=body
            ).execute()
            
            updated_cells = result.get('updates', {}).get('updatedCells', 0)
            logger.info(f"Appended {updated_cells} cells to {range_name}")
            return True
            
        except HttpError as e:
            logger.error(f"Error appending to sheet: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error appending to sheet: {str(e)}")
            return False
    
    def clear_sheet(self, spreadsheet_id: str, range_name: str) -> bool:
        """
        Clear data from a Google Sheet range
        
        Args:
            spreadsheet_id: The ID of the spreadsheet
            range_name: The A1 notation range to clear
            
        Returns:
            bool: True if clear successful
        """
        try:
            if not self.service:
                if not self.authenticate():
                    return False
            
            result = self.service.spreadsheets().values().clear(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            logger.info(f"Cleared range {range_name}")
            return True
            
        except HttpError as e:
            logger.error(f"Error clearing sheet: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error clearing sheet: {str(e)}")
            return False
    
    def get_sheet_info(self, spreadsheet_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a spreadsheet
        
        Args:
            spreadsheet_id: The ID of the spreadsheet
            
        Returns:
            Dict containing spreadsheet metadata
        """
        try:
            if not self.service:
                if not self.authenticate():
                    return None
            
            result = self.service.spreadsheets().get(
                spreadsheetId=spreadsheet_id
            ).execute()
            
            return {
                'title': result.get('properties', {}).get('title', 'Unknown'),
                'sheets': [
                    {
                        'id': sheet['properties']['sheetId'],
                        'title': sheet['properties']['title'],
                        'gridProperties': sheet['properties'].get('gridProperties', {})
                    }
                    for sheet in result.get('sheets', [])
                ]
            }
            
        except HttpError as e:
            logger.error(f"Error getting sheet info: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting sheet info: {str(e)}")
            return None
    
    def create_sheet(self, spreadsheet_id: str, sheet_name: str) -> bool:
        """
        Create a new sheet in the spreadsheet
        
        Args:
            spreadsheet_id: The ID of the spreadsheet
            sheet_name: Name for the new sheet
            
        Returns:
            bool: True if sheet created successfully
        """
        try:
            if not self.service:
                if not self.authenticate():
                    return False
            
            request_body = {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': sheet_name
                        }
                    }
                }]
            }
            
            result = self.service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=request_body
            ).execute()
            
            logger.info(f"Created new sheet: {sheet_name}")
            return True
            
        except HttpError as e:
            if "already exists" in str(e).lower():
                logger.info(f"Sheet {sheet_name} already exists")
                return True
            logger.error(f"Error creating sheet: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error creating sheet: {str(e)}")
            return False

# Global instance
_sheets_service = None

def get_sheets_service(credentials_path: Optional[str] = None) -> GoogleSheetsService:
    """Get or create Google Sheets service instance"""
    global _sheets_service
    if _sheets_service is None:
        _sheets_service = GoogleSheetsService(credentials_path)
    return _sheets_service
