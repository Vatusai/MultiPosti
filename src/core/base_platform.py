from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging

class BaseSocialPlatform(ABC):
    """
    Abstract base class for all social media platforms
    """
    
    def __init__(self, credentials_manager):
        """
        Initialize platform with credentials manager
        
        Args:
            credentials_manager: CredentialsManager instance
        """
        self.credentials_manager = credentials_manager
        self.platform_name = self.get_platform_name()
        self.logger = logging.getLogger(f"{__name__}.{self.platform_name}")
        self._authenticated = False
        self._credentials = None
    
    @abstractmethod
    def get_platform_name(self) -> str:
        """Return the platform name (e.g., 'youtube', 'facebook', 'tiktok')"""
        pass
    
    @abstractmethod
    def authenticate(self) -> bool:
        """
        Authenticate with the platform
        
        Returns:
            bool: True if authentication successful
        """
        pass
    
    @abstractmethod
    def upload_video(self, video_path: str, title: str, description: str, **kwargs) -> Dict[str, Any]:
        """
        Upload video to platform
        
        Args:
            video_path: Path to video file
            title: Video title
            description: Video description
            **kwargs: Platform-specific parameters
        
        Returns:
            Dict containing upload result
        """
        pass
    
    @abstractmethod
    def get_upload_status(self, upload_id: str) -> Dict[str, Any]:
        """
        Get status of an upload
        
        Args:
            upload_id: Upload identifier
        
        Returns:
            Dict containing status information
        """
        pass
    
    def is_authenticated(self) -> bool:
        """Check if platform is authenticated"""
        return self._authenticated
    
    def get_credentials_path(self) -> Path:
        """Get the credentials directory for this platform"""
        return self.credentials_manager.get_platform_path(self.platform_name)
    
    def save_token(self, token_data: Dict[str, Any]) -> bool:
        """Save authentication token"""
        return self.credentials_manager.save_token(self.platform_name, token_data)
    
    def load_token(self) -> Optional[Dict[str, Any]]:
        """Load authentication token"""
        return self.credentials_manager.load_token(self.platform_name)
    
    def validate_video_file(self, video_path: str) -> bool:
        """
        Validate video file exists and is accessible
        
        Args:
            video_path: Path to video file
        
        Returns:
            bool: True if file is valid
        """
        try:
            video_file = Path(video_path)
            if not video_file.exists():
                self.logger.error(f"Video file not found: {video_path}")
                return False
            
            if not video_file.is_file():
                self.logger.error(f"Path is not a file: {video_path}")
                return False
            
            # Check file size (basic validation)
            file_size = video_file.stat().st_size
            if file_size == 0:
                self.logger.error(f"Video file is empty: {video_path}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating video file {video_path}: {e}")
            return False
    
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported video formats for this platform
        
        Returns:
            List of supported file extensions
        """
        # Default formats - platforms can override
        return ['.mp4', '.mov', '.avi', '.mkv', '.webm']
    
    def prepare_upload_data(self, title: str, description: str, **kwargs) -> Dict[str, Any]:
        """
        Prepare data for upload (validation, formatting)
        
        Args:
            title: Video title
            description: Video description
            **kwargs: Additional parameters
        
        Returns:
            Dict with prepared upload data
        """
        # Basic validation and preparation
        upload_data = {
            'title': title.strip() if title else 'Untitled',
            'description': description.strip() if description else '',
            'timestamp': self._get_current_timestamp(),
            'platform': self.platform_name
        }
        
        # Add any additional kwargs
        upload_data.update(kwargs)
        
        return upload_data
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def log_upload_attempt(self, video_path: str, upload_data: Dict[str, Any]):
        """Log upload attempt for debugging"""
        self.logger.info(f"Attempting upload to {self.platform_name}")
        self.logger.info(f"Video: {video_path}")
        self.logger.info(f"Title: {upload_data.get('title', 'N/A')}")
        self.logger.info(f"Description length: {len(upload_data.get('description', ''))}")
    
    def log_upload_result(self, result: Dict[str, Any]):
        """Log upload result"""
        success = result.get('success', False)
        if success:
            self.logger.info(f"Upload successful to {self.platform_name}")
            if 'video_id' in result:
                self.logger.info(f"Video ID: {result['video_id']}")
        else:
            self.logger.error(f"Upload failed to {self.platform_name}")
            if 'error' in result:
                self.logger.error(f"Error: {result['error']}")
    
    def __str__(self):
        """String representation"""
        auth_status = "authenticated" if self._authenticated else "not authenticated"
        return f"{self.platform_name.title()} Platform ({auth_status})"