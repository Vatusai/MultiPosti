import json
import requests
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from core.base_platform import BaseSocialPlatform
import time


class FacebookPlatform(BaseSocialPlatform):
    """
    Facebook platform implementation using Graph API
    """
    
    def __init__(self, credentials_manager):
        super().__init__(credentials_manager)
        self.base_url = "https://graph.facebook.com/v23.0"
        self.video_base_url = "https://graph-video.facebook.com/v23.0"
        self.access_token = None
        self.page_id = None
        self.app_id = None
        
    def get_platform_name(self) -> str:
        """Return platform name"""
        return "facebook"
    
    def authenticate(self) -> bool:
        """
        Verifica si el token existe y no ha expirado.
        Carga access_token, page_id, ig_user_id
        
        Returns:
            bool: True si está todo listo, False si falta algo
        """
        try:
            token_data = self.load_token()
            if not token_data:
                self.logger.error("No se encontró token de Facebook. Por favor configura la autenticación primero.")
                return False
            
            # Check required fields
            required_fields = ['access_token', 'page_id', 'app_id']
            missing_fields = []
            
            for field in required_fields:
                if field not in token_data:
                    missing_fields.append(field)
            
            if missing_fields:
                self.logger.error(f"Faltan campos requeridos en el token: {', '.join(missing_fields)}")
                return False
            
            self.access_token = token_data['access_token']
            self.page_id = token_data['page_id']
            self.app_id = token_data['app_id']
            
            # Test authentication by making a simple API call
            if self._test_authentication():
                self._authenticated = True
                self.logger.info("Autenticación de Facebook exitosa")
                return True
            else:
                self.logger.error("Falló la prueba de autenticación de Facebook")
                return False
                
        except Exception as e:
            self.logger.error(f"Error durante la autenticación de Facebook: {e}")
            return False
    
    def _test_authentication(self) -> bool:
        """
        Test if current access token is valid
        """
        try:
            params = {
                'access_token': self.access_token,
                'fields': 'id,name'
            }
            
            # Test with page info endpoint
            response = requests.get(
                f"{self.base_url}/{self.page_id}",
                params=params,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            self.logger.error(f"Authentication test failed: {e}")
            return False
    
    def upload_video(self, video_path: str, title: str, description: str, hashtags: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
        """
        Upload video to Facebook page.
        
        Args:
            video_path: Path to video file
            title: Video title
            description: Video description
            hashtags: List of hashtags (optional)
        
        Returns:
            Dict containing upload result
        """
        try:
            # Validate inputs
            if not self._authenticated:
                if not self.authenticate():
                    return {"success": False, "error": "Falló la autenticación"}
            
            if not self.validate_video_file(video_path):
                return {"success": False, "error": "Archivo de video inválido"}
            
            # Prepare upload data
            upload_data = self.prepare_upload_data(title, description, hashtags=hashtags)
            self.log_upload_attempt(video_path, upload_data)
            
            # Construir texto combinado
            combined_text = self._format_combined_text(title, description, hashtags)
            
            # Upload video using resumable upload API and then publish
            print("[UPLOAD] Subiendo video a Facebook usando API de subida reanudable...")
            result = self._upload_video_resumable(video_path, title, combined_text)
            
            if result.get("success"):
                print("[SUCCESS] Video publicado en Facebook")
                self.log_upload_result(result)
                return result
            else:
                print(f"[ERROR] Error en Facebook: {result.get('error', 'Error desconocido')}")
                self.log_upload_result(result)
                return result
                
        except Exception as e:
            error_msg = f"Error subiendo video a Facebook: {e}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def _upload_video_resumable(self, video_path: str, title: str, description: str) -> Dict[str, Any]:
        """
        Upload video using Facebook's resumable upload API and then publish it.
        
        Process:
        1. Start upload session
        2. Upload video file
        3. Publish video with the file handle
        """
        try:
            # Step 1: Start upload session
            upload_session = self._start_upload_session(video_path)
            if not upload_session.get("success"):
                return upload_session
            
            upload_session_id = upload_session["session_id"]
            
            # Step 2: Upload the file
            file_handle_result = self._upload_file(upload_session_id, video_path)
            if not file_handle_result.get("success"):
                return file_handle_result
            
            file_handle = file_handle_result["file_handle"]
            
            # Step 3: Publish the video
            publish_result = self._publish_video(file_handle, title, description)
            return publish_result
            
        except Exception as e:
            error_msg = f"Error en subida reanudable: {e}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def _start_upload_session(self, video_path: str) -> Dict[str, Any]:
        """
        Step 1: Start upload session
        POST /{app_id}/uploads
        """
        try:
            file_size = os.path.getsize(video_path)
            file_name = os.path.basename(video_path)
            
            params = {
                'file_name': file_name,
                'file_length': str(file_size),
                'file_type': 'video/mp4',
                'access_token': self.access_token
            }
            
            url = f"{self.base_url}/{self.app_id}/uploads"
            response = requests.post(url, params=params, timeout=30)
            
            if response.status_code == 200:
                response_data = response.json()
                session_id = response_data.get('id')
                
                if session_id and session_id.startswith('upload:'):
                    return {
                        "success": True,
                        "session_id": session_id
                    }
                else:
                    return {"success": False, "error": f"ID de sesión inválido: {session_id}"}
            else:
                error_msg = f"Error iniciando sesión de subida: {response.status_code} - {response.text}"
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            return {"success": False, "error": f"Error iniciando sesión: {e}"}
    
    def _upload_file(self, upload_session_id: str, video_path: str) -> Dict[str, Any]:
        """
        Step 2: Upload file to the session
        POST /upload:{session_id}
        """
        try:
            url = f"{self.base_url}/{upload_session_id}"
            
            headers = {
                'Authorization': f'OAuth {self.access_token}',
                'file_offset': '0'
            }
            
            with open(video_path, 'rb') as video_file:
                response = requests.post(
                    url,
                    headers=headers,
                    data=video_file,
                    timeout=600  # 10 minutes for large files
                )
            
            if response.status_code == 200:
                response_data = response.json()
                file_handle = response_data.get('h')
                
                if file_handle:
                    return {
                        "success": True,
                        "file_handle": file_handle
                    }
                else:
                    return {"success": False, "error": "No se recibió identificador de archivo"}
            else:
                error_msg = f"Error subiendo archivo: {response.status_code} - {response.text}"
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            return {"success": False, "error": f"Error en subida de archivo: {e}"}
    
    def _publish_video(self, file_handle: str, title: str, description: str) -> Dict[str, Any]:
        """
        Step 3: Publish video using the uploaded file handle
        POST /{page_id}/videos
        """
        try:
            url = f"{self.video_base_url}/{self.page_id}/videos"
            
            data = {
                'access_token': self.access_token,
                'title': title[:100],  # Facebook title limit
                'description': description[:60000],  # Facebook description limit
                'fbuploader_video_file_chunk': file_handle
            }
            
            response = requests.post(url, data=data, timeout=60)
            
            if response.status_code == 200:
                response_data = response.json()
                return {
                    "success": True,
                    "video_id": response_data.get('id'),
                    "platform": "facebook"
                }
            else:
                error_msg = f"Error publicando video: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            error_msg = f"Error en publicación: {e}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def _resume_upload_session(self, upload_session_id: str) -> Dict[str, Any]:
        """
        Resume an interrupted upload session
        GET /upload:{session_id}
        """
        try:
            url = f"{self.base_url}/{upload_session_id}"
            
            headers = {
                'Authorization': f'OAuth {self.access_token}'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                response_data = response.json()
                return {
                    "success": True,
                    "session_id": response_data.get('id'),
                    "file_offset": response_data.get('file_offset', 0)
                }
            else:
                error_msg = f"Error obteniendo estado de sesión: {response.status_code} - {response.text}"
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            return {"success": False, "error": f"Error reanudando sesión: {e}"}
    
    def _upload_file_with_offset(self, upload_session_id: str, video_path: str, file_offset: int) -> Dict[str, Any]:
        """
        Upload file from a specific offset (for resumable uploads)
        POST /upload:{session_id}
        """
        try:
            url = f"{self.base_url}/{upload_session_id}"
            
            headers = {
                'Authorization': f'OAuth {self.access_token}',
                'file_offset': str(file_offset)
            }
            
            with open(video_path, 'rb') as video_file:
                # Seek to the offset position
                video_file.seek(file_offset)
                
                response = requests.post(
                    url,
                    headers=headers,
                    data=video_file,
                    timeout=600  # 10 minutes for large files
                )
            
            if response.status_code == 200:
                response_data = response.json()
                file_handle = response_data.get('h')
                
                if file_handle:
                    return {
                        "success": True,
                        "file_handle": file_handle
                    }
                else:
                    return {"success": False, "error": "No se recibió identificador de archivo"}
            else:
                error_msg = f"Error subiendo archivo con offset: {response.status_code} - {response.text}"
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            return {"success": False, "error": f"Error en subida con offset: {e}"}
    
    
    def _format_combined_text(self, title: str, description: str, hashtags: Optional[List[str]] = None) -> str:
        """
        Construir un texto combinado (title + description + hashtags).
        Los hashtags deben ser formateados automáticamente con #.
        """
        parts = []
        
        # Add title if provided
        if title and title.strip():
            parts.append(title.strip())
        
        # Add description if provided
        if description and description.strip():
            parts.append(description.strip())
        
        # Add hashtags if provided
        if hashtags:
            formatted_hashtags = []
            for tag in hashtags:
                tag = tag.strip()
                if tag and not tag.startswith('#'):
                    tag = f"#{tag}"
                if tag:
                    formatted_hashtags.append(tag)
            
            if formatted_hashtags:
                parts.append(' '.join(formatted_hashtags))
        
        # Join all parts with double newline
        final_text = '\n\n'.join(parts)
        
        return final_text
    
    
    def get_upload_status(self, upload_id: str) -> Dict[str, Any]:
        """
        Get status of a video upload
        
        Args:
            upload_id: The video_id from upload response
        
        Returns:
            Dict containing status information
        """
        try:
            if not self._authenticated:
                if not self.authenticate():
                    return {"success": False, "error": "Authentication failed"}
            
            params = {
                'access_token': self.access_token,
                'fields': 'id,title,description,created_time,permalink_url,status'
            }
            
            response = requests.get(
                f"{self.base_url}/{upload_id}",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "status_data": response.json()
                }
            else:
                error_msg = f"Failed to get upload status: {response.status_code} - {response.text}"
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            error_msg = f"Error getting upload status: {e}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def get_supported_formats(self) -> List[str]:
        """
        Get supported video formats for Facebook
        
        Returns:
            List of supported file extensions
        """
        # Facebook supports most common video formats
        return ['.mp4', '.mov', '.avi', '.wmv', '.flv', '.webm', '.mkv', '.3gp']
    
    def prepare_upload_data(self, title: str, description: str, **kwargs) -> Dict[str, Any]:
        """
        Prepare upload data specific to Facebook
        """
        upload_data = super().prepare_upload_data(title, description, **kwargs)
        
        # Facebook-specific validation
        hashtags = kwargs.get('hashtags', [])
        if hashtags and not isinstance(hashtags, list):
            hashtags = [hashtags]
        
        upload_data['hashtags'] = hashtags
        upload_data['combined_text'] = self._format_combined_text(title, description, hashtags)
        
        return upload_data
    
    def get_page_info(self) -> Dict[str, Any]:
        """
        Get information about the connected Facebook page
        
        Returns:
            Dict containing page information
        """
        try:
            if not self._authenticated:
                if not self.authenticate():
                    return {"success": False, "error": "Authentication failed"}
            
            params = {
                'access_token': self.access_token,
                'fields': 'id,name,username,category,followers_count,fan_count'
            }
            
            response = requests.get(
                f"{self.base_url}/{self.page_id}",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "page_info": response.json()
                }
            else:
                error_msg = f"Failed to get page info: {response.status_code} - {response.text}"
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            error_msg = f"Error getting page info: {e}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}