import json
import requests
from pathlib import Path
from typing import Dict, Any, Optional, List
from core.base_platform import BaseSocialPlatform


class TikTokPlatform(BaseSocialPlatform):
    """
    TikTok platform implementation using Content Posting API
    """
    
    def __init__(self, credentials_manager):
        super().__init__(credentials_manager)
        self.base_url = "https://open.tiktokapis.com"
        self.access_token = None
        self.open_id = None
        
    def get_platform_name(self) -> str:
        """Return platform name"""
        return "tiktok"
    
    def authenticate(self) -> bool:
        """
        Load authentication token from credentials file
        
        Returns:
            bool: True if authentication successful
        """
        try:
            token_data = self.load_token()
            if not token_data:
                self.logger.error("No TikTok token found. Please run TikTok authentication first.")
                return False
            
            # Check required fields
            required_fields = ['access_token', 'open_id']
            for field in required_fields:
                if field not in token_data:
                    self.logger.error(f"Missing required field in token: {field}")
                    return False
            
            self.access_token = token_data['access_token']
            self.open_id = token_data['open_id']
            
            # Test authentication by making a simple API call
            if self._test_authentication():
                self._authenticated = True
                self.logger.info("TikTok authentication successful")
                return True
            else:
                self.logger.error("TikTok authentication test failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Error during TikTok authentication: {e}")
            return False
    
    def _test_authentication(self) -> bool:
        """
        Test if current access token is valid
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Use user info endpoint to test auth
            response = requests.get(
                f"{self.base_url}/v2/user/info/",
                headers=headers,
                params={'fields': 'open_id,username'},
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            self.logger.error(f"Authentication test failed: {e}")
            return False
    
    def upload_video(self, video_path: str, title: str, description: str, hashtags: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
        """
        Upload video to TikTok using the Content Posting API
        
        Args:
            video_path: Path to video file
            title: Video title
            description: Video description
            hashtags: List of hashtags (optional)
        
        Returns:
            Dict containing upload result
        """
        try:
            # Validate inputs
            if not self._authenticated:
                if not self.authenticate():
                    return {"success": False, "error": "Authentication failed"}
            
            if not self.validate_video_file(video_path):
                return {"success": False, "error": "Invalid video file"}
            
            # Prepare upload data
            upload_data = self.prepare_upload_data(title, description, hashtags=hashtags)
            self.log_upload_attempt(video_path, upload_data)
            
            # Step 1: Initialize upload session
            print("Inicializando subida...")
            init_response = self._initialize_upload()
            if not init_response.get('success'):
                return init_response
            
            upload_url = init_response['upload_url']
            video_id = init_response['video_id']
            
            # Step 2: Upload video file
            print("Subiendo archivo de video...")
            upload_response = self._upload_file(upload_url, video_path)
            if not upload_response.get('success'):
                return upload_response
            
            print("Video cargado con éxito")
            
            # Step 3: Publish video
            print("Publicando video...")
            final_description = self._format_description(title, description, hashtags)
            publish_response = self._publish_video(video_id, final_description)
            
            if publish_response.get('success'):
                print("Video publicado con éxito")
                result = {
                    "success": True,
                    "platform": "tiktok",
                    "video_id": video_id,
                    "publish_id": publish_response.get('publish_id'),
                    "message": "Video uploaded successfully to TikTok"
                }
                self.log_upload_result(result)
                return result
            else:
                return publish_response
                
        except Exception as e:
            error_msg = f"Error uploading video to TikTok: {e}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def _initialize_upload(self) -> Dict[str, Any]:
        """
        Step 1: Initialize upload session with TikTok
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            data = {
                "source": "file",
                "upload_type": "video"
            }
            
            response = requests.post(
                f"{self.base_url}/v2/video/init/",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                return {
                    "success": True,
                    "upload_url": response_data['data']['upload_url'],
                    "video_id": response_data['data']['video_id']
                }
            else:
                error_msg = f"Failed to initialize upload: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            error_msg = f"Error initializing upload: {e}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def _upload_file(self, upload_url: str, video_path: str) -> Dict[str, Any]:
        """
        Step 2: Upload video file to TikTok's storage
        """
        try:
            with open(video_path, 'rb') as video_file:
                response = requests.put(
                    upload_url,
                    data=video_file,
                    timeout=300  # 5 minutes for large files
                )
            
            if response.status_code in [200, 201]:
                return {"success": True}
            else:
                error_msg = f"Failed to upload file: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            error_msg = f"Error uploading file: {e}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def _publish_video(self, video_id: str, description: str) -> Dict[str, Any]:
        """
        Step 3: Publish the uploaded video
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            data = {
                "video_id": video_id,
                "description": description[:2200]  # TikTok limit: 2200 characters
            }
            
            response = requests.post(
                f"{self.base_url}/v2/video/publish/",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                return {
                    "success": True,
                    "publish_id": response_data['data'].get('publish_id')
                }
            else:
                error_msg = f"Failed to publish video: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            error_msg = f"Error publishing video: {e}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def _format_description(self, title: str, description: str, hashtags: Optional[List[str]] = None) -> str:
        """
        Format description with title, description and hashtags for TikTok
        """
        parts = []
        
        # Add title if provided
        if title and title.strip():
            parts.append(title.strip())
        
        # Add description if provided
        if description and description.strip():
            parts.append(description.strip())
        
        # Add hashtags if provided
        if hashtags:
            formatted_hashtags = []
            for tag in hashtags:
                tag = tag.strip()
                if tag and not tag.startswith('#'):
                    tag = f"#{tag}"
                if tag:
                    formatted_hashtags.append(tag)
            
            if formatted_hashtags:
                parts.append(' '.join(formatted_hashtags))
        
        # Join all parts with double newline
        final_description = '\n\n'.join(parts)
        
        # Ensure we don't exceed TikTok's 2200 character limit
        if len(final_description) > 2200:
            final_description = final_description[:2197] + "..."
            
        return final_description
    
    def get_upload_status(self, upload_id: str) -> Dict[str, Any]:
        """
        Get status of a video upload/publication
        
        Args:
            upload_id: The publish_id or video_id from upload response
        
        Returns:
            Dict containing status information
        """
        try:
            if not self._authenticated:
                if not self.authenticate():
                    return {"success": False, "error": "Authentication failed"}
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{self.base_url}/v2/video/list/",
                headers=headers,
                params={'fields': 'id,title,create_time,share_url,embed_html'},
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "status_data": response.json()
                }
            else:
                error_msg = f"Failed to get upload status: {response.status_code} - {response.text}"
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            error_msg = f"Error getting upload status: {e}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def get_supported_formats(self) -> List[str]:
        """
        Get supported video formats for TikTok
        
        Returns:
            List of supported file extensions
        """
        return ['.mp4', '.mov', '.mpeg', '.3gp', '.avi']
    
    def prepare_upload_data(self, title: str, description: str, **kwargs) -> Dict[str, Any]:
        """
        Prepare upload data specific to TikTok
        """
        upload_data = super().prepare_upload_data(title, description, **kwargs)
        
        # TikTok-specific validation
        hashtags = kwargs.get('hashtags', [])
        if hashtags and not isinstance(hashtags, list):
            hashtags = [hashtags]
        
        upload_data['hashtags'] = hashtags
        upload_data['formatted_description'] = self._format_description(title, description, hashtags)
        
        return upload_data