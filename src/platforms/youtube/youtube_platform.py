import os
import json
from typing import Dict, Any, Optional, List
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from core.base_platform import BaseSocialPlatform

class YouTubePlatform(BaseSocialPlatform):
    """
    YouTube platform implementation
    """
    
    # YouTube API scopes
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    
    def __init__(self, credentials_manager):
        """Initialize YouTube platform"""
        super().__init__(credentials_manager)
        self.youtube_service = None
        self.client_secrets_file = None
    
    def get_platform_name(self) -> str:
        """Return platform name"""
        return 'youtube'
    
    def authenticate(self) -> bool:
        """
        Authenticate with YouTube using OAuth 2.0
        
        Returns:
            bool: True if authentication successful
        """
        try:
            # Get client secrets file path
            self.client_secrets_file = self.get_credentials_path() / 'client_secret.json'
            
            if not self.client_secrets_file.exists():
                self.logger.error(f"Client secrets file not found: {self.client_secrets_file}")
                return False
            
            creds = None
            
            # Load existing token
            token_data = self.load_token()
            if token_data:
                creds = Credentials.from_authorized_user_info(token_data, self.SCOPES)
            
            # If no valid credentials, get new ones
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    self.logger.info("Refreshing expired token...")
                    creds.refresh(Request())
                else:
                    self.logger.info("Starting OAuth flow...")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(self.client_secrets_file), self.SCOPES)
                    creds = flow.run_local_server(port=0, open_browser=True)
                
                # Save the credentials
                token_data = {
                    'token': creds.token,
                    'refresh_token': creds.refresh_token,
                    'token_uri': creds.token_uri,
                    'client_id': creds.client_id,
                    'client_secret': creds.client_secret,
                    'scopes': creds.scopes
                }
                self.save_token(token_data)
                self.logger.info("Token saved successfully")
            
            # Build YouTube service
            self.youtube_service = build('youtube', 'v3', credentials=creds)
            self._authenticated = True
            self._credentials = creds
            
            self.logger.info("YouTube authentication successful")
            return True
            
        except Exception as e:
            self.logger.error(f"YouTube authentication failed: {e}")
            self._authenticated = False
            return False
    
    def upload_video(self, video_path: str, title: str, description: str, **kwargs) -> Dict[str, Any]:
        """
        Upload video to YouTube
        
        Args:
            video_path: Path to video file
            title: Video title
            description: Video description
            **kwargs: Additional parameters (tags, privacy, category_id, etc.)
        
        Returns:
            Dict containing upload result
        """
        if not self.is_authenticated():
            return {'success': False, 'error': 'Not authenticated'}
        
        if not self.validate_video_file(video_path):
            return {'success': False, 'error': 'Invalid video file'}
        
        try:
            # Prepare upload data
            upload_data = self.prepare_upload_data(title, description, **kwargs)
            self.log_upload_attempt(video_path, upload_data)
            
            # Build video metadata
            body = {
                'snippet': {
                    'title': upload_data['title'],
                    'description': upload_data['description'],
                    'tags': upload_data.get('tags', []),
                    'categoryId': upload_data.get('category_id', '22')  # Default: People & Blogs
                },
                'status': {
                    'privacyStatus': upload_data.get('privacy', 'private'),  # private, public, unlisted
                    'selfDeclaredMadeForKids': upload_data.get('made_for_kids', False)
                }
            }
            
            # Create media upload
            media = MediaFileUpload(
                video_path,
                chunksize=-1,  # Upload in a single chunk
                resumable=True,
                mimetype='video/*'
            )
            
            # Execute upload
            insert_request = self.youtube_service.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = self._resumable_upload(insert_request)
            
            if response:
                result = {
                    'success': True,
                    'video_id': response['id'],
                    'video_url': f"https://www.youtube.com/watch?v={response['id']}",
                    'title': response['snippet']['title'],
                    'platform': self.platform_name,
                    'upload_time': self._get_current_timestamp()
                }
                self.log_upload_result(result)
                return result
            else:
                result = {'success': False, 'error': 'Upload failed - no response'}
                self.log_upload_result(result)
                return result
                
        except HttpError as e:
            error_msg = f"YouTube API error: {e}"
            self.logger.error(error_msg)
            return {'success': False, 'error': error_msg}
        
        except Exception as e:
            error_msg = f"Unexpected error during upload: {e}"
            self.logger.error(error_msg)
            return {'success': False, 'error': error_msg}
    
    def get_upload_status(self, upload_id: str) -> Dict[str, Any]:
        """
        Get status of a YouTube video
        
        Args:
            upload_id: YouTube video ID
        
        Returns:
            Dict containing video status information
        """
        if not self.is_authenticated():
            return {'success': False, 'error': 'Not authenticated'}
        
        try:
            response = self.youtube_service.videos().list(
                part='status,snippet,processingDetails',
                id=upload_id
            ).execute()
            
            if response['items']:
                video = response['items'][0]
                return {
                    'success': True,
                    'video_id': upload_id,
                    'status': video['status'],
                    'title': video['snippet']['title'],
                    'processing_details': video.get('processingDetails', {}),
                    'privacy_status': video['status']['privacyStatus']
                }
            else:
                return {'success': False, 'error': 'Video not found'}
                
        except HttpError as e:
            return {'success': False, 'error': f"API error: {e}"}
    
    def get_supported_formats(self) -> List[str]:
        """Get YouTube supported video formats"""
        return ['.mp4', '.mov', '.avi', '.wmv', '.flv', '.webm', '.mkv']
    
    def _resumable_upload(self, insert_request):
        """
        Handle resumable upload with retry logic
        """
        response = None
        error = None
        retry = 0
        max_retries = 3
        
        while response is None:
            try:
                self.logger.info(f"Uploading video... (attempt {retry + 1}/{max_retries + 1})")
                status, response = insert_request.next_chunk()
                
                if response is not None:
                    if 'id' in response:
                        self.logger.info(f"Video uploaded successfully. Video ID: {response['id']}")
                    else:
                        self.logger.error(f"Upload failed with unexpected response: {response}")
                        
            except HttpError as e:
                if e.resp.status in [500, 502, 503, 504]:
                    self.logger.warning(f"Retryable error {e.resp.status}: {e}")
                    error = f"Server error {e.resp.status}: {e}"
                else:
                    self.logger.error(f"Non-retryable error: {e}")
                    raise e
                    
            except Exception as e:
                self.logger.error(f"Unexpected error during upload: {e}")
                error = str(e)
                break
            
            if error is not None:
                retry += 1
                if retry > max_retries:
                    self.logger.error(f"Maximum retries exceeded. Last error: {error}")
                    break
                else:
                    import time
                    sleep_time = 2 ** retry
                    self.logger.info(f"Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                    error = None
        
        return response