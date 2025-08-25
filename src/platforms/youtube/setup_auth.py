"""
YouTube Authentication Setup Script
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path so we can import our modules
src_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(src_path))

from core.credentials_manager import CredentialsManager
from platforms.youtube.youtube_platform import YouTubePlatform

def setup_youtube_authentication():
    """
    Interactive setup for YouTube authentication
    """
    print("=== YOUTUBE AUTHENTICATION SETUP ===")
    print()
    
    # Initialize credentials manager
    credentials_manager = CredentialsManager()
    youtube = YouTubePlatform(credentials_manager)
    
    # Check if client_secret.json exists
    client_secret_path = youtube.get_credentials_path() / 'client_secret.json'
    
    if not client_secret_path.exists():
        print("STEP 1: Client Secret File Missing")
        print("=" * 40)
        print(f"You need to place your client_secret.json file in:")
        print(f"{client_secret_path}")
        print()
        print("To get this file:")
        print("1. Go to Google Cloud Console (https://console.cloud.google.com/)")
        print("2. Select your project")
        print("3. Go to APIs & Services > Credentials")
        print("4. Download the OAuth 2.0 Client ID JSON file")
        print("5. Rename it to 'client_secret.json'")
        print("6. Place it in the credentials/youtube/ folder")
        print()
        
        input("Press Enter after you've placed the client_secret.json file...")
        
        if not client_secret_path.exists():
            print("ERROR: client_secret.json still not found!")
            return False
    
    print("STEP 2: Authentication Process")
    print("=" * 40)
    print("Starting OAuth 2.0 authentication...")
    print("- Your browser will open")
    print("- Sign in to your Google account")
    print("- Grant permissions to your application")
    print("- Return to this terminal when complete")
    print()
    
    # Attempt authentication
    success = youtube.authenticate()
    
    if success:
        print()
        print("=== AUTHENTICATION SUCCESSFUL ===")
        print("✓ OAuth 2.0 flow completed")
        print("✓ Access token obtained and saved")
        print("✓ YouTube API access granted")
        print()
        print(f"Credentials saved in: {youtube.get_credentials_path()}")
        print()
        print("You can now use the YouTube platform for uploading videos!")
        return True
    else:
        print()
        print("=== AUTHENTICATION FAILED ===")
        print("✗ Could not complete authentication")
        print()
        print("Troubleshooting:")
        print("- Check your internet connection")
        print("- Verify client_secret.json is valid")
        print("- Ensure your Google Cloud project has YouTube API enabled")
        print("- Check that OAuth consent screen is configured")
        return False

def test_authentication():
    """
    Test that authentication is working
    """
    print("=== TESTING AUTHENTICATION ===")
    
    credentials_manager = CredentialsManager()
    youtube = YouTubePlatform(credentials_manager)
    
    # Load existing credentials
    token_data = youtube.load_token()
    if not token_data:
        print("✗ No token found. Run setup first.")
        return False
    
    # Test authentication
    if youtube.authenticate():
        print("✓ Authentication test successful")
        print(f"✓ Platform: {youtube}")
        return True
    else:
        print("✗ Authentication test failed")
        return False

def main():
    """
    Main setup function
    """
    print("YOUTUBE PLATFORM SETUP")
    print("=" * 50)
    print()
    
    while True:
        print("Choose an option:")
        print("1. Setup new authentication")
        print("2. Test existing authentication") 
        print("3. Exit")
        print()
        
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == '1':
            print()
            setup_youtube_authentication()
            
        elif choice == '2':
            print()
            test_authentication()
            
        elif choice == '3':
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice. Please try again.")
        
        print()
        print("-" * 50)
        print()

if __name__ == '__main__':
    main()