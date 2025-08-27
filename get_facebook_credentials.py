#!/usr/bin/env python3
"""
Script to help get correct Facebook credentials for video posting
"""

import requests
import json

def get_facebook_credentials():
    """Get correct Facebook credentials from current user token"""
    
    # Load current token
    with open('credentials/facebook/facebook_token.json', 'r') as f:
        token_data = json.load(f)
    
    access_token = token_data['access_token']
    
    print("Getting Facebook credentials...")
    print("=" * 40)
    
    # Get user info
    print("\n1. Current User Info:")
    user_response = requests.get(
        f"https://graph.facebook.com/v23.0/me",
        params={'access_token': access_token, 'fields': 'id,name'}
    )
    
    if user_response.status_code == 200:
        user_data = user_response.json()
        print(f"   User ID: {user_data.get('id')}")
        print(f"   Name: {user_data.get('name')}")
    else:
        print(f"   Error: {user_response.status_code} - {user_response.text}")
        return
    
    # Get managed pages
    print("\n2. Managed Pages:")
    pages_response = requests.get(
        f"https://graph.facebook.com/v23.0/me/accounts",
        params={'access_token': access_token}
    )
    
    if pages_response.status_code == 200:
        pages_data = pages_response.json()
        pages = pages_data.get('data', [])
        
        if pages:
            print(f"   Found {len(pages)} managed page(s):")
            for i, page in enumerate(pages):
                print(f"   {i+1}. {page.get('name')} (ID: {page.get('id')})")
                print(f"      Category: {page.get('category', 'Unknown')}")
                print(f"      Access Token: {page.get('access_token', 'N/A')[:50]}...")
                print()
        else:
            print("   No managed pages found")
            print("   You need to be an admin of a Facebook page to post videos")
    else:
        print(f"   Error: {pages_response.status_code} - {pages_response.text}")
    
    # Get app info (if available)
    print("\n3. App Information:")
    print("   To get your App ID, visit: https://developers.facebook.com/apps/")
    print("   Your app ID should be a numeric value like: 123456789012345")
    
    # Analyze current token type
    print("\n4. Token Analysis:")
    debug_response = requests.get(
        f"https://graph.facebook.com/v23.0/debug_token",
        params={
            'input_token': access_token,
            'access_token': access_token
        }
    )
    
    if debug_response.status_code == 200:
        debug_data = debug_response.json()
        token_info = debug_data.get('data', {})
        print(f"   Token Type: {token_info.get('type', 'Unknown')}")
        print(f"   App ID: {token_info.get('app_id', 'Unknown')}")
        print(f"   Valid: {token_info.get('is_valid', False)}")
        print(f"   Expires: {token_info.get('expires_at', 'Never')}")
        
        # Check scopes
        scopes = token_info.get('scopes', [])
        required_scopes = ['pages_show_list', 'pages_read_engagement', 'pages_manage_posts']
        print(f"\n   Current Scopes: {', '.join(scopes) if scopes else 'None'}")
        print(f"   Required Scopes: {', '.join(required_scopes)}")
        
        missing_scopes = [scope for scope in required_scopes if scope not in scopes]
        if missing_scopes:
            print(f"   Missing Scopes: {', '.join(missing_scopes)}")
        else:
            print("   ✓ All required scopes present")
            
        # Save app_id if found
        app_id = token_info.get('app_id')
        if app_id:
            print(f"\n   Found App ID: {app_id}")
    else:
        print(f"   Error debugging token: {debug_response.status_code}")

if __name__ == "__main__":
    get_facebook_credentials()