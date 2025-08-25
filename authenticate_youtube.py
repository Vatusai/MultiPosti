import os
import json
import webbrowser
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Permisos necesarios para subir y administrar videos
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def authenticate_youtube():
    """
    Autentica con YouTube usando OAuth 2.0 y guarda los tokens.
    Retorna las credenciales autenticadas.
    """
    creds = None

    # Si ya hay token guardado
    if os.path.exists('token.json'):
        print("Token existente encontrado, verificando...")
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # Si no hay token o es inválido
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Token expirado, renovando...")
            creds.refresh(Request())
        else:
            print("Iniciando flujo de autenticacion...")
            print("Se abrira tu navegador para autorizar la aplicacion")
            
            # Usar el archivo de credenciales de cliente
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            
            # Ejecutar el servidor local para recibir el código de autorización
            creds = flow.run_local_server(port=8080, open_browser=True)

        # Guardar el token para uso futuro
        with open('token.json', 'w') as token_file:
            token_file.write(creds.to_json())
        print("Token guardado en token.json")

    print("Autenticacion completa")
    return creds

def main():
    """
    Función principal para ejecutar la autenticación
    """
    try:
        print("Iniciando autenticacion para YouTube Data API")
        print("=" * 50)
        
        # Verificar que existe el archivo de credenciales
        if not os.path.exists('client_secret.json'):
            print("Error: No se encontro el archivo client_secret.json")
            print("Por favor, copia el archivo de credenciales al directorio actual")
            return
        
        # Autenticar
        credentials = authenticate_youtube()
        
        print("=" * 50)
        print("Listo! Ya puedes usar la API de YouTube")
        print("Los tokens estan guardados en token.json")
        
    except Exception as e:
        print(f"Error durante la autenticacion: {str(e)}")
        print("Verifica que:")
        print("   - El archivo client_secret.json este presente")
        print("   - Tengas conexion a internet")
        print("   - El puerto 8080 este disponible")

if __name__ == '__main__':
    main()