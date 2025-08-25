import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Permisos necesarios para subir y administrar videos
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def setup_youtube_authentication():
    """
    Configura la autenticación de YouTube paso a paso
    """
    print("=== CONFIGURACION DE AUTENTICACION YOUTUBE ===")
    print()
    
    # Verificar archivo de credenciales
    if not os.path.exists('client_secret.json'):
        print("ERROR: No se encontro client_secret.json")
        print("Asegurate de que el archivo este en el directorio actual")
        return False
    
    print("1. Archivo client_secret.json encontrado ✓")
    
    # Verificar si ya existe token
    if os.path.exists('token.json'):
        print("2. Token existente encontrado")
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            if creds and creds.valid:
                print("   El token es valido ✓")
                return True
            elif creds and creds.expired and creds.refresh_token:
                print("   Token expirado, renovando...")
                creds.refresh(Request())
                with open('token.json', 'w') as token_file:
                    token_file.write(creds.to_json())
                print("   Token renovado exitosamente ✓")
                return True
        except Exception as e:
            print(f"   Error con token existente: {e}")
            print("   Creando nuevo token...")
    
    # Crear nuevo token
    print("2. Iniciando proceso de autorizacion...")
    print("   INSTRUCCIONES:")
    print("   - Se abrira tu navegador")
    print("   - Inicia sesion con tu cuenta de Google")
    print("   - Autoriza el acceso a YouTube")
    print("   - La pagina mostrara un codigo de confirmacion")
    print()
    
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secret.json', SCOPES)
        
        # Usar puerto diferente por si 8080 está ocupado
        creds = flow.run_local_server(port=0, open_browser=True)
        
        # Guardar credenciales
        with open('token.json', 'w') as token_file:
            token_file.write(creds.to_json())
            
        print("3. Autenticacion completada exitosamente ✓")
        print("4. Token guardado en token.json ✓")
        
        return True
        
    except Exception as e:
        print(f"ERROR durante la autenticacion: {e}")
        print()
        print("SOLUCION DE PROBLEMAS:")
        print("- Verifica tu conexion a internet")
        print("- Asegurate de que ningun antivirus bloquee Python")
        print("- Intenta cerrar otros programas que usen el puerto 8080")
        return False

def test_authentication():
    """
    Prueba que la autenticación funcione correctamente
    """
    if not os.path.exists('token.json'):
        print("No hay token para probar")
        return False
    
    try:
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if creds and creds.valid:
            print("✓ Token valido - Listo para usar YouTube API")
            return True
        else:
            print("✗ Token invalido")
            return False
    except Exception as e:
        print(f"✗ Error probando token: {e}")
        return False

if __name__ == '__main__':
    print("CONFIGURADOR DE AUTENTICACION YOUTUBE")
    print("=====================================")
    print()
    
    success = setup_youtube_authentication()
    
    if success:
        print()
        print("=== RESUMEN ===")
        print("✓ Autenticacion configurada correctamente")
        print("✓ Archivo token.json creado")
        print("✓ Listo para subir videos a YouTube")
        print()
        print("SIGUIENTE PASO:")
        print("- Usa el token.json en tus scripts de subida")
        print("- El token se renueva automaticamente cuando sea necesario")
        
        # Probar autenticación
        print()
        print("Probando autenticacion...")
        test_authentication()
        
    else:
        print()
        print("=== ERROR ===")
        print("✗ No se pudo completar la autenticacion")
        print("Revisa los mensajes de error arriba")