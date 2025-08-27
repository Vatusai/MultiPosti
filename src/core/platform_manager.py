"""
Platform Manager - Central hub for managing all social media platforms
"""

import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from .credentials_manager import CredentialsManager
from .base_platform import BaseSocialPlatform

class PlatformManager:
    """
    Manages multiple social media platforms
    """
    
    def __init__(self, credentials_path: str = None):
        """
        Initialize platform manager
        
        Args:
            credentials_path: Path to credentials directory
        """
        self.credentials_manager = CredentialsManager(credentials_path)
        self.platforms: Dict[str, BaseSocialPlatform] = {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize available platforms
        self._initialize_platforms()
    
    def _initialize_platforms(self):
        """Initialize all available platform implementations"""
        try:
            # Import and register YouTube platform - TEMPORARILY DISABLED
            # from platforms.youtube.youtube_platform import YouTubePlatform
            # self.register_platform('youtube', YouTubePlatform)
            
            # Import and register TikTok platform
            from platforms.tiktok.tiktok_platform import TikTokPlatform
            self.register_platform('tiktok', TikTokPlatform)
            
            # Import and register Facebook platform
            from platforms.facebook.facebook_platform import FacebookPlatform
            self.register_platform('facebook', FacebookPlatform)
            
        except ImportError as e:
            self.logger.warning(f"Some platforms could not be imported: {e}")
    
    def register_platform(self, name: str, platform_class):
        """
        Register a platform class
        
        Args:
            name: Platform name
            platform_class: Platform class (subclass of BaseSocialPlatform)
        """
        try:
            platform_instance = platform_class(self.credentials_manager)
            self.platforms[name] = platform_instance
            self.logger.info(f"Registered platform: {name}")
        except Exception as e:
            self.logger.error(f"Failed to register platform {name}: {e}")
    
    def get_platform(self, name: str) -> Optional[BaseSocialPlatform]:
        """
        Get platform instance by name
        
        Args:
            name: Platform name
        
        Returns:
            Platform instance or None if not found
        """
        return self.platforms.get(name.lower())
    
    def get_available_platforms(self) -> List[str]:
        """Get list of available platform names"""
        return list(self.platforms.keys())
    
    def authenticate_platform(self, platform_name: str) -> bool:
        """
        Authenticate with a specific platform
        
        Args:
            platform_name: Name of platform to authenticate
        
        Returns:
            bool: True if authentication successful
        """
        platform = self.get_platform(platform_name)
        if not platform:
            self.logger.error(f"Platform not found: {platform_name}")
            return False
        
        return platform.authenticate()
    
    def authenticate_all_platforms(self) -> Dict[str, bool]:
        """
        Authenticate with all registered platforms
        
        Returns:
            Dict mapping platform names to authentication success status
        """
        results = {}
        for name, platform in self.platforms.items():
            try:
                results[name] = platform.authenticate()
            except Exception as e:
                self.logger.error(f"Authentication failed for {name}: {e}")
                results[name] = False
        
        return results
    
    def upload_video_to_platform(self, platform_name: str, video_path: str, 
                                title: str, description: str, **kwargs) -> Dict[str, Any]:
        """
        Upload video to specific platform
        
        Args:
            platform_name: Target platform name
            video_path: Path to video file
            title: Video title
            description: Video description
            **kwargs: Platform-specific parameters
        
        Returns:
            Dict containing upload result
        """
        platform = self.get_platform(platform_name)
        if not platform:
            return {'success': False, 'error': f'Platform not found: {platform_name}'}
        
        if not platform.is_authenticated():
            self.logger.warning(f"Platform {platform_name} not authenticated, attempting authentication...")
            if not platform.authenticate():
                return {'success': False, 'error': f'Authentication failed for {platform_name}'}
        
        return platform.upload_video(video_path, title, description, **kwargs)
    
    def upload_video_to_multiple_platforms(self, platforms: List[str], video_path: str,
                                         title: str, description: str, **kwargs) -> Dict[str, Any]:
        """
        Upload video to multiple platforms
        
        Args:
            platforms: List of platform names
            video_path: Path to video file  
            title: Video title
            description: Video description
            **kwargs: Platform-specific parameters
        
        Returns:
            Dict mapping platform names to upload results
        """
        results = {}
        
        for platform_name in platforms:
            self.logger.info(f"Uploading to {platform_name}...")
            result = self.upload_video_to_platform(
                platform_name, video_path, title, description, **kwargs
            )
            results[platform_name] = result
            
            if result['success']:
                self.logger.info(f"Upload to {platform_name} successful")
            else:
                self.logger.error(f"Upload to {platform_name} failed: {result.get('error', 'Unknown error')}")
        
        return results
    
    def get_platform_status(self, platform_name: str) -> Dict[str, Any]:
        """
        Get status information for a platform
        
        Args:
            platform_name: Platform name
        
        Returns:
            Dict containing platform status
        """
        platform = self.get_platform(platform_name)
        if not platform:
            return {'exists': False, 'error': 'Platform not found'}
        
        return {
            'exists': True,
            'authenticated': platform.is_authenticated(),
            'platform_name': platform.platform_name,
            'credentials_path': str(platform.get_credentials_path()),
            'supported_formats': platform.get_supported_formats()
        }
    
    def get_all_platform_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status for all registered platforms"""
        status = {}
        for name in self.platforms.keys():
            status[name] = self.get_platform_status(name)
        return status
    
    def backup_all_credentials(self) -> bool:
        """Create backup of all platform credentials"""
        return self.credentials_manager.backup_credentials()
    
    def setup_logging(self, log_level: str = 'INFO', log_file: str = None):
        """
        Setup logging configuration
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            log_file: Optional log file path
        """
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        if log_file:
            logging.basicConfig(
                level=getattr(logging, log_level.upper()),
                format=log_format,
                handlers=[
                    logging.FileHandler(log_file),
                    logging.StreamHandler()
                ]
            )
        else:
            logging.basicConfig(
                level=getattr(logging, log_level.upper()),
                format=log_format
            )
        
        self.logger.info("Logging configured")
    
    def __str__(self):
        """String representation"""
        platform_list = ', '.join(self.platforms.keys())
        return f"PlatformManager with platforms: {platform_list}"