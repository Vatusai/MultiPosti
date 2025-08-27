# Regenerar Token de Facebook para DigiViolin

## 🔍 Problema Identificado:
Tu access token actual **NO incluye permisos para la página DigiViolin**, aunque seas el admin.

## 📋 Información Actual:
- **Tu perfil**: `faog2694` (https://www.facebook.com/faog2694/)
- **Tu User ID**: `10238533643543614`
- **Página DigiViolin**: `61580060690937` (https://www.facebook.com/profile.php?id=61580060690937)
- **App ID**: `1438267127386307`
- **Token actual**: Válido pero sin acceso a DigiViolin

## 🛠️ Solución: Generar Nuevo Token

### Paso 1: Ir a Facebook Graph API Explorer
1. **Visita**: https://developers.facebook.com/tools/explorer/
2. **Asegúrate** de estar logueado como `faog2694`

### Paso 2: Configurar el Token
1. **Selecciona tu App**: `1438267127386307` (en el dropdown superior)
2. **Click en "Get User Access Token"**
3. **Selecciona estos permisos**:
   - ✅ `pages_show_list`
   - ✅ `pages_read_engagement` 
   - ✅ `pages_manage_posts`
   - ✅ `pages_manage_metadata`
   - ✅ `public_profile`

### Paso 3: Generar Token
1. **Click "Generate Access Token"**
2. **Autoriza la aplicación**
3. **Copia el nuevo token** (será un string largo que empiece con "EAA...")

### Paso 4: Verificar el Token
Antes de usarlo, verifica que funciona:
1. **Pega el token** en el campo "Access Token"
2. **En el campo de consulta**, pon: `me/accounts`
3. **Click "Submit"**
4. **Verifica** que aparezca DigiViolin en la respuesta

### Paso 5: Actualizar Credenciales
Reemplaza el `access_token` en `credentials/facebook/facebook_token.json`:

```json
{
  "access_token": "TU_NUEVO_TOKEN_AQUI",
  "app_id": "1438267127386307",
  "user_id": "10238533643543614",
  "user_name": "Fabian Orozco González", 
  "page_id": "61580060690937",
  "created_at": 1699999999
}
```

### Paso 6: Probar
```bash
python test_digiviolin_page.py
```

## ⚠️ Importante:
- **Usa el mismo perfil** (`faog2694`) para generar el token
- **Incluye TODOS los permisos** necesarios
- **El token debe generarse CON acceso a DigiViolin**

## 🔧 Si Sigues Teniendo Problemas:
1. **Verifica** que realmente eres admin de DigiViolin desde `faog2694`
2. **Espera 5-10 minutos** después de cambiar permisos de página
3. **Prueba generar el token desde**: https://developers.facebook.com/tools/accesstoken/