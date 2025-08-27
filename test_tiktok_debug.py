#!/usr/bin/env python3
"""
Debug script for TikTok authentication and upload testing
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.platform_manager import PlatformManager
import requests
import json


def debug_tiktok_authentication():
    """Debug TikTok authentication step by step"""
    print("TikTok Authentication Debug")
    print("=" * 40)
    
    # Initialize platform manager
    platform_manager = PlatformManager(credentials_path="credentials")
    
    # Get TikTok platform
    tiktok_platform = platform_manager.get_platform('tiktok')
    
    if not tiktok_platform:
        print("ERROR: TikTok platform not found")
        return
    
    print("SUCCESS: TikTok platform loaded")
    
    # Load token manually to debug
    try:
        token_data = tiktok_platform.load_token()
        if not token_data:
            print("ERROR: No token found")
            return
        
        print("SUCCESS: Token loaded")
        print(f"Token fields: {list(token_data.keys())}")
        print(f"Access token starts with: {token_data.get('access_token', '')[:20]}...")
        print(f"Open ID: {token_data.get('open_id', 'Not found')}")
        print(f"Scope: {token_data.get('scope', 'Not found')}")
        print(f"Expires in: {token_data.get('expires_in', 'Not found')} seconds")
        
        # Test API call directly
        print("\nTesting API call directly...")
        headers = {
            'Authorization': f'Bearer {token_data["access_token"]}',
            'Content-Type': 'application/json'
        }
        
        # Test user info endpoint
        print("Calling /v2/user/info/...")
        response = requests.get(
            "https://open.tiktokapis.com/v2/user/info/",
            headers=headers,
            params={'fields': 'open_id,username'},
            timeout=10
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Response text: {response.text}")
        
        if response.status_code == 200:
            print("SUCCESS: Direct API call successful")
        else:
            print("ERROR: Direct API call failed")
            
        # Now test platform authentication
        print("\nTesting platform authentication...")
        auth_result = tiktok_platform.authenticate()
        print(f"Authentication result: {auth_result}")
        
    except Exception as e:
        print(f"ERROR: Error during debug: {e}")
        import traceback
        traceback.print_exc()


def debug_token_scopes():
    """Check what scopes are available and required"""
    print("\nTikTok Scopes Debug")
    print("=" * 40)
    
    print("Current token scope: user.info.basic")
    print("\nRequired scopes for video upload:")
    print("- video.upload (Create and upload videos)")
    print("- video.publish (Publish videos)")
    print("- user.info.basic (Basic user info)")
    
    print("\nPOTENTIAL ISSUE: Current token only has 'user.info.basic'")
    print("For video upload, you likely need 'video.upload' and 'video.publish' scopes")


def main():
    """Main debug function"""
    debug_tiktok_authentication()
    debug_token_scopes()


if __name__ == "__main__":
    main()