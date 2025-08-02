"""
Google Drive Service for Workflow Integration
"""
import io
import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

try:
    import gspread
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
    from googleapiclient.errors import HttpError
    GOOGLE_DRIVE_AVAILABLE = True
    print("✅ Google Drive service imported successfully")
except ImportError as e:
    GOOGLE_DRIVE_AVAILABLE = False
    print(f"❌ Google Drive service import failed: {e}")


class GoogleDriveService:
    """Service for Google Drive integration"""
    
    def __init__(self, credentials_path: str = None):
        if credentials_path is None:
            credentials_path = "credentials.json"  # Default path
            
        self.credentials_path = credentials_path
        self.scope = [
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/drive.file'
        ]
        self.credentials = None
        self.service = None
        self.authenticated = False
    
    async def authenticate(self) -> bool:
        """Authenticate with Google Drive API"""
        try:
            if not os.path.exists(self.credentials_path):
                print(f"❌ Credentials file not found: {self.credentials_path}")
                return False
                
            self.credentials = Credentials.from_service_account_file(
                self.credentials_path, scopes=self.scope
            )
            self.service = build('drive', 'v3', credentials=self.credentials)
            self.authenticated = True
            print("✅ Google Drive authentication successful")
            return True
            
        except Exception as e:
            print(f"❌ Google Drive authentication failed: {e}")
            self.authenticated = False
            return False
    
    async def upload_file(
        self, 
        file_content: bytes, 
        filename: str, 
        folder_id: str = None,
        mimetype: str = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """Upload a file to Google Drive"""
        try:
            if not self.authenticated or not self.service:
                return False, {"error": "Not authenticated"}
            
            # Auto-detect mimetype if not provided
            if not mimetype:
                if filename.endswith('.txt'):
                    mimetype = 'text/plain'
                elif filename.endswith('.json'):
                    mimetype = 'application/json'
                elif filename.endswith('.csv'):
                    mimetype = 'text/csv'
                elif filename.endswith('.pdf'):
                    mimetype = 'application/pdf'
                elif filename.endswith('.png'):
                    mimetype = 'image/png'
                elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
                    mimetype = 'image/jpeg'
                else:
                    mimetype = 'application/octet-stream'
            
            # Prepare file metadata
            file_metadata = {
                'name': filename
            }
            
            # Add to specific folder if provided
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            # Create media upload
            media = MediaIoBaseUpload(
                io.BytesIO(file_content),
                mimetype=mimetype,
                resumable=True
            )
            
            # Upload the file
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,size,mimeType,createdTime,webViewLink,webContentLink'
            ).execute()
            
            result = {
                "operation": "upload_success",
                "file_info": {
                    "file_id": file.get('id'),
                    "filename": file.get('name'),
                    "size": file.get('size'),
                    "mime_type": file.get('mimeType'),
                    "created_time": file.get('createdTime'),
                    "web_view_link": file.get('webViewLink'),
                    "download_link": file.get('webContentLink'),
                    "folder_id": folder_id
                },
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
            
            print(f"✅ File uploaded to Google Drive: {filename}")
            return True, result
            
        except HttpError as e:
            error_msg = f"Google Drive API error: {e}"
            print(f"❌ {error_msg}")
            return False, {"error": error_msg}
        except Exception as e:
            error_msg = f"Upload error: {str(e)}"
            print(f"❌ {error_msg}")
            return False, {"error": error_msg}
    
    async def create_folder(self, folder_name: str, parent_folder_id: str = None) -> Tuple[bool, Dict[str, Any]]:
        """Create a folder in Google Drive"""
        try:
            if not self.authenticated or not self.service:
                return False, {"error": "Not authenticated"}
            
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_folder_id:
                file_metadata['parents'] = [parent_folder_id]
            
            folder = self.service.files().create(
                body=file_metadata,
                fields='id,name,createdTime,webViewLink'
            ).execute()
            
            result = {
                "operation": "folder_created",
                "folder_info": {
                    "folder_id": folder.get('id'),
                    "folder_name": folder.get('name'),
                    "created_time": folder.get('createdTime'),
                    "web_view_link": folder.get('webViewLink'),
                    "parent_folder_id": parent_folder_id
                },
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
            
            print(f"✅ Folder created in Google Drive: {folder_name}")
            return True, result
            
        except Exception as e:
            error_msg = f"Folder creation error: {str(e)}"
            print(f"❌ {error_msg}")
            return False, {"error": error_msg}
    
    async def list_files(self, folder_id: str = None, max_results: int = 100) -> Tuple[bool, Dict[str, Any]]:
        """List files in Google Drive"""
        try:
            if not self.authenticated or not self.service:
                return False, {"error": "Not authenticated"}
            
            query = "trashed=false"
            if folder_id:
                query += f" and '{folder_id}' in parents"
            
            results = self.service.files().list(
                q=query,
                pageSize=max_results,
                fields="nextPageToken, files(id,name,size,mimeType,createdTime,modifiedTime,webViewLink)"
            ).execute()
            
            files = results.get('files', [])
            
            result = {
                "operation": "list_success",
                "files": files,
                "count": len(files),
                "folder_id": folder_id,
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
            
            print(f"✅ Listed {len(files)} files from Google Drive")
            return True, result
            
        except Exception as e:
            error_msg = f"List files error: {str(e)}"
            print(f"❌ {error_msg}")
            return False, {"error": error_msg}
    
    async def delete_file(self, file_id: str) -> Tuple[bool, Dict[str, Any]]:
        """Delete a file from Google Drive"""
        try:
            if not self.authenticated or not self.service:
                return False, {"error": "Not authenticated"}
            
            self.service.files().delete(fileId=file_id).execute()
            
            result = {
                "operation": "delete_success",
                "file_id": file_id,
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
            
            print(f"✅ File deleted from Google Drive: {file_id}")
            return True, result
            
        except Exception as e:
            error_msg = f"Delete error: {str(e)}"
            print(f"❌ {error_msg}")
            return False, {"error": error_msg}
