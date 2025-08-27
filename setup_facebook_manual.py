#!/usr/bin/env python3
"""
Manual Facebook Authentication Setup
Simple script to help set up Facebook authentication manually
"""

print("Manual Facebook Authentication Setup")
print("=" * 50)

print("\n1. Go to Facebook Developer Console: https://developers.facebook.com/")
print("2. Select your app (MultiPosti)")
print("3. Go to Graph API Explorer: https://developers.facebook.com/tools/explorer/")

print("\n4. In Graph API Explorer:")
print("   - Select your app from dropdown")
print("   - Click 'Generate Access Token'")
print("   - Select these permissions:")
print("     * pages_manage_posts")
print("     * pages_read_engagement") 
print("     * pages_show_list")
print("     * instagram_basic")
print("     * instagram_content_publish")

print("\n5. Copy the generated User Access Token")
print("6. Go to Access Token Debugger: https://developers.facebook.com/tools/debug/accesstoken/")
print("7. Paste your token and click 'Debug'")
print("8. Click 'Extend Access Token' to get a long-lived token")

print("\n9. Copy the long-lived token and run this:")
print("   python -c \"import json; token=input('Paste long-lived token: '); print('Token saved!') if open('credentials/facebook/facebook_token.json', 'w').write(json.dumps({'access_token': token, 'page_id': 'YOUR_PAGE_ID', 'ig_user_id': 'YOUR_IG_USER_ID', 'created_at': 1699999999})) else None\"")

print("\n10. You'll also need your Page ID and Instagram Business Account ID")
print("    Get these from Graph API Explorer by querying '/me/accounts' and '/PAGE_ID?fields=instagram_business_account'")

print("\nAlternatively, let's try a simpler approach...")

# Simple token update
print("\nEnter your details:")
try:
    access_token = input("Long-lived User Access Token: ")
    page_id = input("Facebook Page ID: ")
    ig_user_id = input("Instagram Business Account ID (optional): ")
    
    if access_token and page_id:
        import json
        from pathlib import Path
        
        token_data = {
            "access_token": access_token,
            "page_id": page_id,
            "ig_user_id": ig_user_id if ig_user_id else None,
            "created_at": int(time.time()) if 'time' in dir() else 1699999999
        }
        
        credentials_dir = Path("credentials/facebook")
        credentials_dir.mkdir(parents=True, exist_ok=True)
        
        token_path = credentials_dir / "facebook_token.json"
        with open(token_path, 'w') as f:
            json.dump(token_data, f, indent=2)
        
        print(f"\nCredentials saved to: {token_path}")
        print("You can now test the upload again!")
        
except KeyboardInterrupt:
    print("\nSetup cancelled.")
except Exception as e:
    print(f"\nError: {e}")