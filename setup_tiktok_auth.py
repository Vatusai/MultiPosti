#!/usr/bin/env python3
"""
TikTok Authentication Setup
Simple script to help set up TikTok authentication
"""

import json
import webbrowser
import urllib.parse
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import requests

class TikTokOAuthHandler(BaseHTTPRequestHandler):
    """HTTP handler to capture TikTok OAuth callback"""
    
    def do_GET(self):
        """Handle GET request from OAuth callback"""
        query_params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        
        if 'code' in query_params:
            self.server.auth_code = query_params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            response_html = """
            <html><body>
            <h2>Success! TikTok authentication code received</h2>
            <p>You can close this window and return to the terminal.</p>
            <script>setTimeout(function(){window.close()}, 3000);</script>
            </body></html>
            """
            self.wfile.write(response_html.encode('utf-8'))
        elif 'error' in query_params:
            error = query_params.get('error_description', ['Unknown error'])[0]
            self.server.auth_error = error
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            error_html = f"""
            <html><body>
            <h2>Authentication Error</h2>
            <p>{error}</p>
            </body></html>
            """
            self.wfile.write(error_html.encode('utf-8'))
        
        threading.Thread(target=self.server.shutdown).start()
    
    def log_message(self, format, *args):
        pass

def load_tiktok_credentials():
    """Load TikTok app credentials"""
    creds_path = Path("credentials/tiktok/client_secret.json")
    if not creds_path.exists():
        print(f"ERROR: Credentials file not found: {creds_path}")
        return None
    
    try:
        with open(creds_path, 'r') as f:
            creds = json.load(f)
        return creds
    except Exception as e:
        print(f"ERROR: Failed to load credentials: {e}")
        return None

def start_oauth_flow(client_key, redirect_uri):
    """Start TikTok OAuth flow"""
    # TikTok OAuth URL
    auth_url = "https://www.tiktok.com/auth/authorize/"
    
    params = {
        'client_key': client_key,
        'scope': 'user.info.basic,video.list,video.upload',
        'response_type': 'code',
        'redirect_uri': redirect_uri,
        'state': 'tiktok_auth_state'
    }
    
    auth_url_full = auth_url + '?' + urllib.parse.urlencode(params)
    
    print(f"Opening browser for TikTok authorization...")
    print(f"URL: {auth_url_full}")
    webbrowser.open(auth_url_full)
    
    # Start local server to capture callback
    server = HTTPServer(('localhost', 8080), TikTokOAuthHandler)
    server.auth_code = None
    server.auth_error = None
    
    print("Waiting for TikTok authorization...")
    print("(Complete the authorization in your browser)")
    
    server.serve_forever()
    
    if hasattr(server, 'auth_code') and server.auth_code:
        print("Authorization code received!")
        return server.auth_code
    elif hasattr(server, 'auth_error'):
        print(f"Authorization failed: {server.auth_error}")
        return None
    else:
        print("No authorization code received")
        return None

def exchange_code_for_token(client_key, client_secret, auth_code, redirect_uri):
    """Exchange authorization code for access token"""
    token_url = "https://open.tiktokapis.com/v2/oauth/token/"
    
    data = {
        'client_key': client_key,
        'client_secret': client_secret,
        'code': auth_code,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri
    }
    
    try:
        response = requests.post(token_url, data=data, timeout=30)
        
        if response.status_code == 200:
            token_data = response.json()
            print("Access token obtained successfully!")
            return token_data
        else:
            print(f"Failed to get access token: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Error exchanging code for token: {e}")
        return None

def save_token(token_data):
    """Save token data to file"""
    try:
        token_path = Path("credentials/tiktok/tiktok_token.json")
        token_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(token_path, 'w') as f:
            json.dump(token_data, f, indent=2)
        
        print(f"Token saved to: {token_path}")
        return True
        
    except Exception as e:
        print(f"Error saving token: {e}")
        return False

def main():
    print("TikTok Authentication Setup")
    print("=" * 30)
    
    # Load credentials
    creds = load_tiktok_credentials()
    if not creds:
        return 1
    
    client_key = creds.get('client_key')
    client_secret = creds.get('client_secret')
    redirect_uri = creds.get('redirect_uri', 'http://localhost:8080/tiktok_callback')
    
    if not all([client_key, client_secret]):
        print("ERROR: Missing client_key or client_secret in credentials")
        return 1
    
    print(f"Client Key: {client_key}")
    print(f"Redirect URI: {redirect_uri}")
    
    # Start OAuth flow
    auth_code = start_oauth_flow(client_key, redirect_uri)
    if not auth_code:
        print("Failed to get authorization code")
        return 1
    
    # Exchange code for token
    token_data = exchange_code_for_token(client_key, client_secret, auth_code, redirect_uri)
    if not token_data:
        print("Failed to get access token")
        return 1
    
    # Save token
    if save_token(token_data):
        print("\nTikTok authentication setup complete!")
        print("You can now upload videos to TikTok using MultiPosti")
        return 0
    else:
        print("Failed to save token")
        return 1

if __name__ == '__main__':
    import sys
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nSetup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)