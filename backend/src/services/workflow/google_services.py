"""
Google Services Integration for Workflow
"""
import asyncio
import io
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import pandas as pd


class GoogleSheetsService:
    """Service for Google Sheets integration"""
    
    def __init__(self, credentials_path: str = None):
        if credentials_path is None:
            credentials_path = "credentials.json"  # Default path
            
        self.credentials_path = credentials_path
        self.scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        self.credentials = None
        self.client = None
        self.authenticated = False
    
    async def authenticate(self) -> bool:
        """Authenticate with Google Sheets API"""
        try:
            import os
            if not os.path.exists(self.credentials_path):
                print(f"❌ Credentials file not found: {self.credentials_path}")
                return False
                
            self.credentials = Credentials.from_service_account_file(
                self.credentials_path, scopes=self.scope
            )
            self.client = gspread.authorize(self.credentials)
            self.authenticated = True
            print("✅ Google Sheets authentication successful")
            return True
            
        except Exception as e:
            print(f"❌ Google Sheets authentication failed: {e}")
            self.authenticated = False
            return False
    
    async def write_to_sheet(
        self, 
        sheet_id: str, 
        sheet_name: str, 
        range_start: str, 
        mode: str, 
        data: List[List[Any]]
    ) -> Tuple[bool, Dict[str, Any]]:
        """Write data to Google Sheets with automatic Prompt column creation"""
        try:
            if not self.authenticated or not self.client:
                return False, {"error": "Not authenticated"}
                
            # Open the spreadsheet
            sheet = self.client.open_by_key(sheet_id)
            
            # Try to get the specific worksheet, create if not exists
            try:
                worksheet = sheet.worksheet(sheet_name)
                print(f"✅ Found existing worksheet: {sheet_name}")
            except gspread.WorksheetNotFound:
                # Create new worksheet
                worksheet = sheet.add_worksheet(title=sheet_name, rows=1000, cols=26)
                print(f"✅ Created new worksheet: {sheet_name}")
            
            # 🎯 NEW: Auto-add Prompt column if needed
            if data and len(data) > 0:
                headers = data[0]  # Assume first row is headers
                existing_headers = []
                
                try:
                    # Get existing headers from worksheet
                    existing_headers = worksheet.row_values(1) if worksheet.row_count > 0 else []
                    print(f"📊 Existing headers: {existing_headers}")
                    print(f"📊 New data headers: {headers}")
                    
                    # Check if we need to add Prompt column
                    if "Prompt" in headers and "Prompt" not in existing_headers:
                        print(f"🎯 Adding Prompt column to worksheet {sheet_name}")
                        
                        # If worksheet is empty or has no headers
                        if not existing_headers:
                            # Write the complete new headers
                            worksheet.update("A1", [headers])
                            print(f"✅ Added complete headers with Prompt column")
                        else:
                            # Find next available column for Prompt
                            next_col_index = len(existing_headers) + 1
                            next_col_letter = chr(ord('A') + next_col_index - 1)
                            
                            # Add Prompt to headers
                            worksheet.update(f"{next_col_letter}1", "Prompt")
                            print(f"✅ Added Prompt column at {next_col_letter}1")
                            
                            # Update existing_headers for data alignment
                            existing_headers.append("Prompt")
                    
                    # Align data with existing worksheet structure
                    if existing_headers and len(existing_headers) != len(headers):
                        print(f"🔧 Aligning data format...")
                        data = self._align_data_with_headers(data, headers, existing_headers)
                        print(f"🔧 Data aligned: {len(data[0]) if data else 0} columns")
                        
                except Exception as header_error:
                    print(f"⚠️ Header alignment error: {header_error}, proceeding with original data")
            
            # Write data based on mode
            if mode == "append":
                # Append rows to the end
                for row in data:
                    worksheet.append_row(row)
            else:
                # Overwrite starting from range_start
                # Parse range_start (e.g., "A1")
                col_letter = ''.join(filter(str.isalpha, range_start))
                row_num = int(''.join(filter(str.isdigit, range_start)))
                
                # Calculate range for update
                end_col_num = ord(col_letter) - ord('A') + len(data[0]) - 1
                end_col_letter = chr(ord('A') + end_col_num)
                end_row_num = row_num + len(data) - 1
                
                range_name = f"{col_letter}{row_num}:{end_col_letter}{end_row_num}"
                worksheet.update(range_name, data)
            
            result = {
                "operation": "write_success",
                "sheet_info": {
                    "sheet_id": sheet_id,
                    "sheet_name": sheet_name,
                    "range": range_start,
                    "mode": mode
                },
                "data_written": {
                    "rows_count": len(data),
                    "columns_count": len(data[0]) if data else 0,
                    "format": "auto",
                    "range_written": range_name if mode != "append" else "appended"
                },
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
            
            return True, result
            
        except Exception as e:
            print(f"❌ Error writing to Google Sheets: {e}")
            import traceback
            print(f"❌ Traceback: {traceback.format_exc()}")
            return False, {"error": str(e)}
    
    def _align_data_with_headers(self, data: List[List[Any]], source_headers: List[str], target_headers: List[str]) -> List[List[Any]]:
        """Align data columns with target worksheet headers"""
        if not data or not source_headers or not target_headers:
            return data
            
        aligned_data = []
        
        # Create mapping from source to target positions
        for row in data:
            aligned_row = [""] * len(target_headers)
            
            for i, source_header in enumerate(source_headers):
                if i < len(row) and source_header in target_headers:
                    target_index = target_headers.index(source_header)
                    aligned_row[target_index] = row[i]
            
            aligned_data.append(aligned_row)
        
        return aligned_data
    
    async def read_sheet(
        self, 
        sheet_id: str, 
        sheet_name: str = None, 
        range_str: str = "A:Z"
    ) -> Tuple[bool, Dict[str, Any]]:
        """Read data from Google Sheets with sheet creation if not exists"""
        try:
            if not self.authenticated or not self.client:
                return False, {"error": "Not authenticated"}
                
            # Open the spreadsheet
            sheet = self.client.open_by_key(sheet_id)
            
            # If no sheet_name specified, use first sheet
            if not sheet_name:
                worksheet = sheet.sheet1
                sheet_name = worksheet.title
            else:
                # Try to get the specific worksheet, create if not exists
                try:
                    worksheet = sheet.worksheet(sheet_name)
                    print(f"✅ Found existing worksheet: {sheet_name}")
                except gspread.WorksheetNotFound:
                    # Create new worksheet
                    worksheet = sheet.add_worksheet(title=sheet_name, rows=1000, cols=26)
                    print(f"✅ Created new worksheet: {sheet_name}")
                    
                    # Add default headers
                    default_headers = ["Column A", "Column B", "Column C", "Column D", "Column E"]
                    worksheet.update("A1:E1", [default_headers])
                    print(f"✅ Added default headers to new worksheet")
            
            # Read data from the specified range
            try:
                # Get all values in the range
                values = worksheet.get(range_str)
                
                if not values:
                    values = []
                
                result = {
                    "operation": "read_success",
                    "sheet_info": {
                        "sheet_id": sheet_id,
                        "sheet_name": sheet_name,
                        "range": range_str,
                        "title": sheet.title
                    },
                    "data": {
                        "values": values,
                        "rows_count": len(values),
                        "columns_count": len(values[0]) if values else 0
                    },
                    "timestamp": datetime.now().isoformat(),
                    "status": "success"
                }
                
                return True, result
                
            except Exception as read_error:
                print(f"❌ Error reading from worksheet: {read_error}")
                return False, {"error": f"Failed to read from worksheet: {str(read_error)}"}
            
        except Exception as e:
            print(f"❌ Error in read_sheet: {e}")
            return False, {"error": str(e)}
    
    async def read_sheet_data(self, sheet_id: str, sheet_range: str = "A:Z") -> List[Dict[str, Any]]:
        """Read data from Google Sheets"""
        try:
            sheet = self.client.open_by_key(sheet_id)
            worksheet = sheet.sheet1  # Use first sheet by default
            
            # Get all records as list of dictionaries
            records = worksheet.get_all_records()
            
            return records
            
        except Exception as e:
            raise Exception(f"Failed to read Google Sheets data: {str(e)}")
    
    def read_sheet_sync(self, sheet_id: str, range_name: str) -> List[List[Any]]:
        """Read raw sheet data (synchronous for compatibility)"""
        try:
            if not self.authenticated or not self.client:
                raise Exception("Not authenticated")
                
            sheet = self.client.open_by_key(sheet_id)
            
            # Parse range for worksheet name
            if '!' in range_name:
                sheet_name, cell_range = range_name.split('!', 1)
                worksheet = sheet.worksheet(sheet_name)
                values = worksheet.get(cell_range)
            else:
                worksheet = sheet.sheet1
                values = worksheet.get(range_name)
            
            return values or []
            
        except Exception as e:
            raise Exception(f"Failed to read sheet data: {str(e)}")
    
    async def update_sheet_row(
        self, 
        sheet_id: str, 
        row_number: int, 
        data: Dict[str, Any],
        columns_mapping: Dict[str, str] = None
    ) -> bool:
        """Update a specific row in Google Sheets"""
        try:
            sheet = self.client.open_by_key(sheet_id)
            worksheet = sheet.sheet1
            
            # Get headers to map column names
            headers = worksheet.row_values(1)
            
            # Update cells based on column mapping
            for column_name, value in data.items():
                if columns_mapping and column_name in columns_mapping:
                    actual_column = columns_mapping[column_name]
                else:
                    actual_column = column_name
                
                if actual_column in headers:
                    col_index = headers.index(actual_column) + 1
                    worksheet.update_cell(row_number, col_index, value)
            
            return True
            
        except Exception as e:
            raise Exception(f"Failed to update Google Sheets row: {str(e)}")
    
    async def append_sheet_row(
        self, 
        sheet_id: str, 
        data: Dict[str, Any]
    ) -> bool:
        """Append a new row to Google Sheets"""
        try:
            sheet = self.client.open_by_key(sheet_id)
            worksheet = sheet.sheet1
            
            # Get headers
            headers = worksheet.row_values(1)
            
            # Create row data based on headers
            row_data = []
            for header in headers:
                row_data.append(data.get(header, ""))
            
            worksheet.append_row(row_data)
            return True
            
        except Exception as e:
            raise Exception(f"Failed to append Google Sheets row: {str(e)}")
    
    async def get_sheet_info(self, sheet_id: str) -> Dict[str, Any]:
        """Get information about the sheet"""
        try:
            sheet = self.client.open_by_key(sheet_id)
            worksheet = sheet.sheet1
            
            return {
                "title": sheet.title,
                "worksheet_title": worksheet.title,
                "row_count": worksheet.row_count,
                "col_count": worksheet.col_count,
                "headers": worksheet.row_values(1) if worksheet.row_count > 0 else []
            }
            
        except Exception as e:
            raise Exception(f"Failed to get Google Sheets info: {str(e)}")


class GoogleDriveService:
    """Service for Google Drive integration"""
    
    def __init__(self, credentials_path: str):
        self.credentials_path = credentials_path
        self.scope = [
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/drive.file'
        ]
        self.credentials = Credentials.from_service_account_file(
            credentials_path, scopes=self.scope
        )
        self.service = build('drive', 'v3', credentials=self.credentials)
    
    async def create_folder(self, folder_name: str, parent_folder_id: str = None) -> str:
        """Create a folder in Google Drive"""
        try:
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_folder_id:
                folder_metadata['parents'] = [parent_folder_id]
            
            folder = self.service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()
            
            return folder.get('id')
            
        except Exception as e:
            raise Exception(f"Failed to create Google Drive folder: {str(e)}")
    
    async def upload_file(
        self, 
        file_data: bytes, 
        file_name: str, 
        mime_type: str,
        folder_id: str = None
    ) -> Dict[str, Any]:
        """Upload a file to Google Drive"""
        try:
            file_metadata = {'name': file_name}
            
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            media = MediaIoBaseUpload(
                io.BytesIO(file_data),
                mimetype=mime_type,
                resumable=True
            )
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,webViewLink,webContentLink'
            ).execute()
            
            # Make the file publicly accessible
            await self._make_file_public(file.get('id'))
            
            return {
                'file_id': file.get('id'),
                'file_name': file.get('name'),
                'web_view_link': file.get('webViewLink'),
                'download_link': file.get('webContentLink')
            }
            
        except Exception as e:
            raise Exception(f"Failed to upload file to Google Drive: {str(e)}")
    
    async def _make_file_public(self, file_id: str):
        """Make a file publicly accessible"""
        try:
            permission = {
                'type': 'anyone',
                'role': 'reader'
            }
            
            self.service.permissions().create(
                fileId=file_id,
                body=permission
            ).execute()
            
        except Exception as e:
            # Log error but don't fail the upload
            print(f"Warning: Could not make file public: {str(e)}")
    
    async def list_files_in_folder(self, folder_id: str) -> List[Dict[str, Any]]:
        """List files in a specific folder"""
        try:
            query = f"'{folder_id}' in parents"
            results = self.service.files().list(
                q=query,
                fields="files(id, name, mimeType, createdTime, size, webViewLink)"
            ).execute()
            
            return results.get('files', [])
            
        except Exception as e:
            raise Exception(f"Failed to list Google Drive files: {str(e)}")
    
    async def delete_file(self, file_id: str) -> bool:
        """Delete a file from Google Drive"""
        try:
            self.service.files().delete(fileId=file_id).execute()
            return True
            
        except Exception as e:
            raise Exception(f"Failed to delete Google Drive file: {str(e)}")
    
    async def get_folder_id_by_name(self, folder_name: str, parent_folder_id: str = None) -> Optional[str]:
        """Find folder ID by name"""
        try:
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
            if parent_folder_id:
                query += f" and '{parent_folder_id}' in parents"
            
            results = self.service.files().list(
                q=query,
                fields="files(id, name)"
            ).execute()
            
            files = results.get('files', [])
            return files[0]['id'] if files else None
            
        except Exception as e:
            raise Exception(f"Failed to find Google Drive folder: {str(e)}")


class GoogleServicesManager:
    """Manager for all Google services"""
    
    def __init__(self, credentials_path: str):
        self.credentials_path = credentials_path
        self.sheets_service = GoogleSheetsService(credentials_path)
        self.drive_service = GoogleDriveService(credentials_path)
    
    async def process_sheet_for_workflow(self, sheet_id: str) -> List[Dict[str, Any]]:
        """Process Google Sheets data for workflow execution"""
        try:
            # Read sheet data
            sheet_data = await self.sheets_service.read_sheet_data(sheet_id)
            
            # Validate and format data for workflow
            processed_data = []
            for row_index, row in enumerate(sheet_data, start=2):  # Start from row 2 (after header)
                if self._is_valid_workflow_row(row):
                    processed_row = {
                        'task_id': f"{sheet_id}_{row_index}_{int(datetime.now().timestamp())}",
                        'sheet_id': sheet_id,
                        'row_number': row_index,
                        'input_description': row.get('description', ''),
                        'input_asset_urls': self._parse_asset_urls(row.get('asset_urls', '')),
                        'output_format': row.get('output_format', 'PNG').upper(),
                        'model_specification': row.get('model_specification', 'OpenAI'),
                        'original_row_data': row
                    }
                    processed_data.append(processed_row)
            
            return processed_data
            
        except Exception as e:
            raise Exception(f"Failed to process Google Sheets for workflow: {str(e)}")
    
    def _is_valid_workflow_row(self, row: Dict[str, Any]) -> bool:
        """Check if a row has valid data for workflow processing"""
        required_fields = ['description', 'output_format', 'model_specification']
        return all(row.get(field) for field in required_fields)
    
    def _parse_asset_urls(self, urls_string: str) -> List[str]:
        """Parse asset URLs from string"""
        if not urls_string:
            return []
        
        # Split by comma or newline and clean up
        urls = [url.strip() for url in urls_string.replace('\n', ',').split(',')]
        return [url for url in urls if url and url.startswith(('http://', 'https://'))]
    
    async def create_workflow_output_folder(self, workflow_instance_id: str) -> str:
        """Create a dedicated folder for workflow outputs"""
        folder_name = f"Workflow_Output_{workflow_instance_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        return await self.drive_service.create_folder(folder_name)
    
    async def store_workflow_file(
        self, 
        file_data: bytes, 
        file_name: str, 
        mime_type: str,
        workflow_folder_id: str
    ) -> Dict[str, Any]:
        """Store a generated file in the workflow folder"""
        return await self.drive_service.upload_file(
            file_data, file_name, mime_type, workflow_folder_id
        )
