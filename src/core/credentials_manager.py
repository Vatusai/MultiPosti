import os
import json
import logging
from pathlib import Path
from typing import Dict, Optional, Any
from abc import ABC, abstractmethod

class CredentialsManager:
    """
    Centralized credentials manager for all social media platforms
    """
    
    def __init__(self, base_path: str = None):
        """
        Initialize credentials manager
        
        Args:
            base_path: Base path for credentials directory
        """
        if base_path is None:
            # Get project root (MultiPosti directory)
            current_dir = Path(__file__).parent.parent.parent
            base_path = current_dir / "credentials"
        
        self.credentials_path = Path(base_path)
        self.credentials_path.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    def get_platform_path(self, platform: str) -> Path:
        """Get the credentials path for a specific platform"""
        platform_path = self.credentials_path / platform.lower()
        platform_path.mkdir(parents=True, exist_ok=True)
        return platform_path
    
    def save_credentials(self, platform: str, credentials: Dict[str, Any], filename: str = None) -> bool:
        """
        Save credentials for a platform
        
        Args:
            platform: Platform name (youtube, facebook, tiktok)
            credentials: Credentials dictionary
            filename: Optional custom filename
        
        Returns:
            bool: Success status
        """
        try:
            platform_path = self.get_platform_path(platform)
            
            if filename is None:
                filename = f"{platform}_credentials.json"
            
            credentials_file = platform_path / filename
            
            with open(credentials_file, 'w') as f:
                json.dump(credentials, f, indent=4)
            
            self.logger.info(f"Saved credentials for {platform} to {credentials_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving credentials for {platform}: {e}")
            return False
    
    def load_credentials(self, platform: str, filename: str = None) -> Optional[Dict[str, Any]]:
        """
        Load credentials for a platform
        
        Args:
            platform: Platform name
            filename: Optional custom filename
        
        Returns:
            Dict or None: Credentials dictionary or None if not found
        """
        try:
            platform_path = self.get_platform_path(platform)
            
            if filename is None:
                filename = f"{platform}_credentials.json"
            
            credentials_file = platform_path / filename
            
            if not credentials_file.exists():
                self.logger.warning(f"Credentials file not found: {credentials_file}")
                return None
            
            with open(credentials_file, 'r') as f:
                credentials = json.load(f)
            
            self.logger.info(f"Loaded credentials for {platform}")
            return credentials
            
        except Exception as e:
            self.logger.error(f"Error loading credentials for {platform}: {e}")
            return None
    
    def save_token(self, platform: str, token_data: Dict[str, Any]) -> bool:
        """
        Save authentication token for a platform
        
        Args:
            platform: Platform name
            token_data: Token data dictionary
        
        Returns:
            bool: Success status
        """
        return self.save_credentials(platform, token_data, f"{platform}_token.json")
    
    def load_token(self, platform: str) -> Optional[Dict[str, Any]]:
        """
        Load authentication token for a platform
        
        Args:
            platform: Platform name
        
        Returns:
            Dict or None: Token data or None if not found
        """
        return self.load_credentials(platform, f"{platform}_token.json")
    
    def get_client_secrets_path(self, platform: str) -> Path:
        """Get the path for client secrets file"""
        platform_path = self.get_platform_path(platform)
        return platform_path / f"client_secret.json"
    
    def get_api_key_path(self, platform: str) -> Path:
        """Get the path for API key file"""
        platform_path = self.get_platform_path(platform)
        return platform_path / f"api_key.txt"
    
    def list_platform_files(self, platform: str) -> list:
        """List all files for a specific platform"""
        try:
            platform_path = self.get_platform_path(platform)
            return [f.name for f in platform_path.iterdir() if f.is_file()]
        except Exception as e:
            self.logger.error(f"Error listing files for {platform}: {e}")
            return []
    
    def backup_credentials(self, platform: str = None) -> bool:
        """
        Create backup of credentials
        
        Args:
            platform: Specific platform to backup, or None for all
        
        Returns:
            bool: Success status
        """
        try:
            backup_path = self.credentials_path / "backups"
            backup_path.mkdir(exist_ok=True)
            
            import shutil
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if platform:
                # Backup specific platform
                platform_path = self.get_platform_path(platform)
                backup_file = backup_path / f"{platform}_backup_{timestamp}.zip"
                shutil.make_archive(backup_file.with_suffix(''), 'zip', platform_path)
            else:
                # Backup all platforms
                backup_file = backup_path / f"all_credentials_backup_{timestamp}.zip"
                shutil.make_archive(backup_file.with_suffix(''), 'zip', self.credentials_path)
            
            self.logger.info(f"Created backup: {backup_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating backup: {e}")
            return False