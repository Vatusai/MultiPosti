#!/usr/bin/env python3
"""
Facebook/Instagram OAuth 2.0 Authentication Setup for MultiPosti
Implements complete OAuth flow to get long-lived tokens for Facebook Pages and Instagram Business
"""

import json
import requests
import webbrowser
import urllib.parse
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

class OAuthHandler(BaseHTTPRequestHandler):
    """HTTP handler to capture OAuth callback"""
    
    def do_GET(self):
        """Handle GET request from OAuth callback"""
        # Parse query parameters
        query_params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        
        if 'code' in query_params:
            # Success - got authorization code
            self.server.auth_code = query_params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            response_html = """
            <html><body>
            <h2>OK: Autenticacion exitosa!</h2>
            <p>Puedes cerrar esta ventana y volver a la terminal.</p>
            <script>setTimeout(function(){window.close()}, 3000);</script>
            </body></html>
            """
            self.wfile.write(response_html.encode('utf-8'))
        elif 'error' in query_params:
            # Error in OAuth flow
            error = query_params.get('error_description', ['Unknown error'])[0]
            self.server.auth_error = error
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            error_html = f"""
            <html><body>
            <h2>ERROR: Error en autenticacion</h2>
            <p>{error}</p>
            </body></html>
            """
            self.wfile.write(error_html.encode('utf-8'))
        
        # Shutdown server after handling request
        threading.Thread(target=self.server.shutdown).start()
    
    def log_message(self, format, *args):
        """Suppress server logs"""
        pass

class FacebookAuthenticator:
    """Facebook/Instagram OAuth 2.0 authenticator"""
    
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v23.0"
        self.oauth_base = "https://www.facebook.com/v23.0/dialog/oauth"
        
        # Load credentials
        self.credentials_dir = Path(__file__).parent.parent.parent.parent / "credentials" / "facebook"
        self.client_secret_path = self.credentials_dir / "client_secret.json"
        self.token_path = self.credentials_dir / "facebook_token.json"
        
        self.app_id = None
        self.app_secret = None
        self.redirect_uri = None
        
        print("Iniciando configuración de Facebook/Instagram OAuth...")
        
    def load_client_credentials(self):
        """Load app credentials from client_secret.json"""
        try:
            if not self.client_secret_path.exists():
                raise FileNotFoundError(f"Archivo de credenciales no encontrado: {self.client_secret_path}")
            
            with open(self.client_secret_path, 'r') as f:
                creds = json.load(f)
            
            self.app_id = creds.get('app_id')
            self.app_secret = creds.get('app_secret')
            self.redirect_uri = creds.get('redirect_uri', 'http://localhost:8080/callback')
            
            if not all([self.app_id, self.app_secret]):
                raise ValueError("app_id y app_secret son requeridos en client_secret.json")
            
            print(f"Credenciales cargadas - App ID: {self.app_id}")
            return True
            
        except Exception as e:
            print(f"Error cargando credenciales: {e}")
            return False
    
    def start_oauth_flow(self):
        """Start OAuth 2.0 authorization flow"""
        print("\n[STEP] Paso 1: Iniciando flujo de autorización...")
        
        # Required permissions for Facebook Pages according to official documentation
        scopes = [
            'pages_show_list',           # List pages user manages
            'pages_manage_posts',        # Create and manage page posts  
            'pages_manage_read_engagement',  # Read engagement data
            'pages_manage_metadata',     # Manage page metadata
            'publish_video'              # Required specifically for video uploads
        ]
        
        # Build authorization URL
        params = {
            'client_id': self.app_id,
            'redirect_uri': self.redirect_uri,
            'scope': ','.join(scopes),
            'response_type': 'code',
            'state': 'multiposti_auth'
        }
        
        auth_url = f"{self.oauth_base}?" + urllib.parse.urlencode(params)
        
        print(f"[BROWSER] Abriendo navegador para autorización...")
        print(f"Si no se abre automáticamente, visita: {auth_url}")
        
        # Start local server to capture callback
        server = HTTPServer(('localhost', 8080), OAuthHandler)
        server.auth_code = None
        server.auth_error = None
        
        # Open browser
        webbrowser.open(auth_url)
        
        print("[WAIT] Esperando autorización... (autoriza la aplicación en el navegador)")
        
        # Handle the OAuth callback
        server.handle_request()
        
        if hasattr(server, 'auth_error') and server.auth_error:
            print(f"ERROR: Error en autorización: {server.auth_error}")
            return None
        
        if hasattr(server, 'auth_code') and server.auth_code:
            print("OK: Código de autorización recibido")
            return server.auth_code
        
        print("ERROR: No se recibió código de autorización")
        return None
    
    def exchange_code_for_token(self, auth_code):
        """Exchange authorization code for access token"""
        print("\n[STEP 2] Intercambiando código por token de acceso...")
        
        try:
            params = {
                'client_id': self.app_id,
                'client_secret': self.app_secret,
                'redirect_uri': self.redirect_uri,
                'code': auth_code
            }
            
            response = requests.get(f"{self.base_url}/oauth/access_token", params=params)
            
            if response.status_code == 200:
                data = response.json()
                short_token = data.get('access_token')
                
                if short_token:
                    print("OK: Token de corta duración obtenido")
                    return short_token
                else:
                    print(f"ERROR: No se encontró access_token en respuesta: {data}")
                    return None
            else:
                print(f"ERROR: Error obteniendo token: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"ERROR: Error en intercambio de código: {e}")
            return None
    
    def get_long_lived_token(self, short_token):
        """Convert short-lived token to long-lived token"""
        print("\n[STEP 3] Convirtiendo a token de larga duración...")
        
        try:
            params = {
                'grant_type': 'fb_exchange_token',
                'client_id': self.app_id,
                'client_secret': self.app_secret,
                'fb_exchange_token': short_token
            }
            
            response = requests.get(f"{self.base_url}/oauth/access_token", params=params)
            
            if response.status_code == 200:
                data = response.json()
                long_token = data.get('access_token')
                expires_in = data.get('expires_in', 'No expiration info')
                
                if long_token:
                    print(f"OK: Token de larga duración obtenido (válido por ~{expires_in} segundos)")
                    return long_token
                else:
                    print(f"ERROR: No se encontró access_token en respuesta: {data}")
                    return None
            else:
                print(f"ERROR: Error obteniendo token de larga duración: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"ERROR: Error convirtiendo token: {e}")
            return None
    
    def get_user_pages(self, access_token):
        """Get Facebook pages managed by user"""
        print("\n[STEP 4] Obteniendo páginas de Facebook...")
        
        try:
            params = {
                'access_token': access_token
            }
            
            response = requests.get(f"{self.base_url}/me/accounts", params=params)
            
            if response.status_code == 200:
                data = response.json()
                pages = data.get('data', [])
                
                if pages:
                    print(f"OK: Se encontraron {len(pages)} páginas:")
                    for i, page in enumerate(pages):
                        print(f"  {i+1}. {page['name']} (ID: {page['id']})")
                    
                    return pages
                else:
                    print("ERROR: No se encontraron páginas. Asegúrate de tener páginas de Facebook administradas.")
                    return []
            else:
                print(f"ERROR: Error obteniendo páginas: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"ERROR: Error obteniendo páginas: {e}")
            return []
    
    def select_page(self, pages):
        """Let user select which page to use"""
        if not pages:
            return None
        
        if len(pages) == 1:
            selected_page = pages[0]
            print(f"📄 Usando única página disponible: {selected_page['name']}")
            return selected_page
        
        print(f"\n📋 Selecciona una página para usar con MultiPosti:")
        
        while True:
            try:
                choice = input(f"Ingresa el número (1-{len(pages)}): ").strip()
                choice_idx = int(choice) - 1
                
                if 0 <= choice_idx < len(pages):
                    selected_page = pages[choice_idx]
                    print(f"OK: Página seleccionada: {selected_page['name']}")
                    return selected_page
                else:
                    print(f"ERROR: Número inválido. Debe ser entre 1 y {len(pages)}")
            except ValueError:
                print("ERROR: Ingresa un número válido")
            except KeyboardInterrupt:
                print("\nERROR: Operación cancelada")
                return None
    
    
    def save_tokens(self, access_token, page_id):
        """Save authentication tokens to file"""
        print("\n[SAVE] Guardando credenciales...")
        
        try:
            # Ensure credentials directory exists
            self.credentials_dir.mkdir(parents=True, exist_ok=True)
            
            token_data = {
                'access_token': access_token,
                'page_id': page_id,
                'created_at': time.time()
            }
            
            with open(self.token_path, 'w') as f:
                json.dump(token_data, f, indent=2)
            
            print(f"OK: Credenciales guardadas en: {self.token_path}")
            return True
            
        except Exception as e:
            print(f"ERROR: Error guardando credenciales: {e}")
            return False
    
    def run_complete_flow(self):
        """Run the complete OAuth authentication flow"""
        print("[READY] Iniciando configuración completa de Facebook para MultiPosti")
        print("=" * 70)
        
        # Step 1: Load credentials
        if not self.load_client_credentials():
            return False
        
        # Step 2: Start OAuth flow
        auth_code = self.start_oauth_flow()
        if not auth_code:
            return False
        
        # Step 3: Exchange for short token
        short_token = self.exchange_code_for_token(auth_code)
        if not short_token:
            return False
        
        # Step 4: Get long-lived token
        long_token = self.get_long_lived_token(short_token)
        if not long_token:
            return False
        
        # Step 5: Get user pages
        pages = self.get_user_pages(long_token)
        if not pages:
            return False
        
        # Step 6: Select page
        selected_page = self.select_page(pages)
        if not selected_page:
            return False
        
        page_id = selected_page['id']
        page_name = selected_page['name']
        
        # Step 7: Save tokens
        success = self.save_tokens(long_token, page_id)
        
        if success:
            print("\n[SUCCESS] Configuración completada exitosamente!")
            print("=" * 50)
            print(f"[PAGE] Página de Facebook: {page_name}")
            print(f"[TOKEN] Access Token: Guardado")
            print(f"[FILE] Archivo: {self.token_path}")
            print("\nOK: MultiPosti ya puede publicar en Facebook!")
            return True
        else:
            print("\nERROR: Error en configuración")
            return False

def main():
    """Main function to run Facebook/Instagram authentication setup"""
    try:
        authenticator = FacebookAuthenticator()
        success = authenticator.run_complete_flow()
        
        if success:
            print("\n[READY] ¡Listo! Ahora puedes usar MultiPosti con Facebook")
            print("Ejecuta: python scripts/main.py list")
        else:
            print("\nERROR: Configuración incompleta. Revisa los errores arriba.")
            return 1
            
    except KeyboardInterrupt:
        print("\nConfiguración cancelada por el usuario")
        return 1
    except Exception as e:
        print(f"\nError inesperado: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())