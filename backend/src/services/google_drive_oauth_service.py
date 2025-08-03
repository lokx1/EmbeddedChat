"""
Google Drive Service with OAuth Support
Alternative to service account for fixing storage quota issue
"""
import os
import json
import asyncio
from typing import Dict, Any, Tuple, Optional, List
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload
from googleapiclient.errors import HttpError

class GoogleDriveOAuthService:
    """Google Drive service using OAuth user credentials"""
    
    SCOPES = [
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/drive'
    ]
    
    def __init__(self):
        self.service = None
        self.credentials = None
        
        # Paths - Fixed to look in correct locations
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # Go up to backend/
        self.token_file = os.path.join(self.base_dir, 'src', 'google_drive_token.json')
        self.credentials_file = os.path.join(self.base_dir, 'oauth_credentials.json')  # OAuth credentials
    
    async def authenticate(self) -> bool:
        """Authenticate using OAuth credentials"""
        try:
            creds = None
            
            # Load existing token
            if os.path.exists(self.token_file):
                creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)
            
            # Refresh or get new credentials
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_file):
                        print(f"❌ Missing credentials.json at: {self.credentials_file}")
                        return False
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, self.SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                
                # Save credentials
                with open(self.token_file, 'w') as token:
                    token.write(creds.to_json())
            
            self.credentials = creds
            self.service = build('drive', 'v3', credentials=creds)
            
            # Test connection
            self.service.files().list(pageSize=1).execute()
            print("✅ Google Drive OAuth authentication successful")
            return True
            
        except Exception as e:
            print(f"❌ OAuth authentication failed: {str(e)}")
            return False
    
    async def upload_file(
        self, 
        file_content: bytes, 
        filename: str, 
        folder_id: Optional[str] = None,
        mimetype: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """Upload file to Google Drive using OAuth"""
        
        if not self.service:
            if not await self.authenticate():
                return False, {"error": "Authentication failed"}
        
        try:
            # Prepare file metadata
            file_metadata = {'name': filename}
            
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            # Auto-detect MIME type if not provided
            if not mimetype:
                if filename.endswith('.json'):
                    mimetype = 'application/json'
                elif filename.endswith('.csv'):
                    mimetype = 'text/csv'
                elif filename.endswith('.txt'):
                    mimetype = 'text/plain'
                else:
                    mimetype = 'application/octet-stream'
            
            # Create media upload
            media = MediaInMemoryUpload(file_content, mimetype=mimetype)
            
            # Upload file
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,size,mimeType,createdTime,webViewLink,webContentLink'
            ).execute()
            
            return True, {
                "file_id": file.get('id'),
                "name": file.get('name'),
                "size": file.get('size'),
                "mime_type": file.get('mimeType'),
                "created_time": file.get('createdTime'),
                "web_view_link": file.get('webViewLink'),
                "web_content_link": file.get('webContentLink'),
                "folder_id": folder_id,
                "upload_method": "oauth"
            }
            
        except HttpError as e:
            error_details = e.error_details[0] if e.error_details else {}
            return False, {
                "error": f"Google Drive API error: {str(e)}",
                "error_code": e.resp.status,
                "error_reason": error_details.get('reason', 'unknown'),
                "error_message": error_details.get('message', str(e))
            }
        except Exception as e:
            return False, {"error": f"Upload error: {str(e)}"}
    
    async def list_files(self, folder_id: Optional[str] = None, max_results: int = 100) -> Tuple[bool, Dict[str, Any]]:
        """List files in a folder"""
        
        if not self.service:
            if not await self.authenticate():
                return False, {"error": "Authentication failed"}
        
        try:
            query = []
            if folder_id:
                query.append(f"'{folder_id}' in parents")
            query.append("trashed=false")
            
            query_string = " and ".join(query)
            
            results = self.service.files().list(
                q=query_string,
                pageSize=max_results,
                fields="nextPageToken, files(id, name, size, mimeType, createdTime, modifiedTime)"
            ).execute()
            
            files = results.get('files', [])
            
            return True, {
                "files": files,
                "count": len(files),
                "folder_id": folder_id
            }
            
        except Exception as e:
            return False, {"error": f"List files error: {str(e)}"}
    
    async def delete_file(self, file_id: str) -> Tuple[bool, Dict[str, Any]]:
        """Delete a file"""
        
        if not self.service:
            if not await self.authenticate():
                return False, {"error": "Authentication failed"}
        
        try:
            self.service.files().delete(fileId=file_id).execute()
            return True, {"file_id": file_id, "status": "deleted"}
            
        except Exception as e:
            return False, {"error": f"Delete error: {str(e)}"}
    
    async def create_folder(self, folder_name: str, parent_folder_id: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
        """Create a new folder"""
        
        if not self.service:
            if not await self.authenticate():
                return False, {"error": "Authentication failed"}
        
        try:
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_folder_id:
                file_metadata['parents'] = [parent_folder_id]
            
            folder = self.service.files().create(
                body=file_metadata,
                fields='id,name,webViewLink'
            ).execute()
            
            return True, {
                "folder_id": folder.get('id'),
                "name": folder.get('name'),
                "web_view_link": folder.get('webViewLink')
            }
            
        except Exception as e:
            return False, {"error": f"Create folder error: {str(e)}"}

# Global instance for OAuth service
oauth_drive_service = GoogleDriveOAuthService()
