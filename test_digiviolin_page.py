#!/usr/bin/env python3
"""
Test DigiViolin page access specifically
"""

import requests
import json

def test_digiviolin_page():
    """Test access to DigiViolin page"""
    
    # Load token
    with open('credentials/facebook/facebook_token.json', 'r') as f:
        token_data = json.load(f)
    
    access_token = token_data['access_token']
    page_id = token_data['page_id']
    
    print("Testing DigiViolin Page Access")
    print("=" * 40)
    print(f"Page ID: {page_id}")
    print(f"Page URL: https://www.facebook.com/profile.php?id={page_id}")
    
    # Test 1: Try to get page info directly
    print("\n1. Testing direct page access...")
    response = requests.get(
        f"https://graph.facebook.com/v23.0/{page_id}",
        params={
            'access_token': access_token,
            'fields': 'id,name,category,can_post'
        }
    )
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Page Name: {data.get('name', 'Unknown')}")
        print(f"   Category: {data.get('category', 'Unknown')}")
        print(f"   Can Post: {data.get('can_post', 'Unknown')}")
    else:
        print(f"   Error: {response.text}")
        
        # Check if it's a permissions issue
        if response.status_code == 403:
            print("   >> This is a PERMISSIONS issue")
            print("   >> You need to be an admin of the DigiViolin page")
        elif response.status_code == 400:
            error_data = response.json()
            error_msg = error_data.get('error', {}).get('message', 'Unknown error')
            print(f"   >> Error details: {error_msg}")
    
    # Test 2: Try to get page access token
    print("\n2. Testing page access token retrieval...")
    response2 = requests.get(
        f"https://graph.facebook.com/v23.0/me/accounts",
        params={'access_token': access_token}
    )
    
    if response2.status_code == 200:
        pages_data = response2.json()
        pages = pages_data.get('data', [])
        digiviolin_page = None
        
        for page in pages:
            if page.get('id') == page_id:
                digiviolin_page = page
                break
        
        if digiviolin_page:
            print("   SUCCESS: DigiViolin page found in managed pages!")
            print(f"   Page Access Token: {digiviolin_page.get('access_token', 'N/A')[:50]}...")
            
            # Save the page access token
            token_data['page_access_token'] = digiviolin_page.get('access_token')
            with open('credentials/facebook/facebook_token.json', 'w') as f:
                json.dump(token_data, f, indent=2)
            print("   Page access token saved to credentials file!")
            
        else:
            print("   DigiViolin page NOT found in managed pages")
            print("   This means you're not an admin of the page")
            
            if pages:
                print(f"   You do manage these pages:")
                for page in pages:
                    print(f"     - {page.get('name')} (ID: {page.get('id')})")
    else:
        print(f"   Error getting managed pages: {response2.text}")
    
    # Test 3: Recommendations
    print("\n3. Recommendations:")
    if response.status_code != 200:
        print("   >> You need to become an admin of the DigiViolin page")
        print("   >> Steps:")
        print("      1. Go to: https://www.facebook.com/profile.php?id=61580060690937")
        print("      2. Make sure you're an admin of this page")
        print("      3. Or ask the current admin to add you as admin")
        print("      4. Then generate a NEW access token that includes this page")
        print("      5. Visit: https://developers.facebook.com/tools/explorer/")
        print("      6. Select your app and request a new User Access Token")
        print("      7. Make sure to include page permissions when generating the token")

if __name__ == "__main__":
    test_digiviolin_page()