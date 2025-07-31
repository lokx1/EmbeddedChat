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
    
    def __init__(self, credentials_path: str):
        self.credentials_path = credentials_path
        self.scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        self.credentials = Credentials.from_service_account_file(
            credentials_path, scopes=self.scope
        )
        self.client = gspread.authorize(self.credentials)
    
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
