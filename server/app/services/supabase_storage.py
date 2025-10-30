import os
import uuid
from datetime import datetime
from typing import Optional
from supabase import create_client, Client
from fastapi import HTTPException, status
from dotenv import load_dotenv

load_dotenv()

class SupabaseStorageService:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")
        self.supabase_service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.bucket_name = os.getenv("SUPABASE_STORAGE_BUCKET", "study-materials")
        self.storage_url = os.getenv("SUPABASE_STORAGE_URL")
        
        # Validate configuration
        if not self.supabase_url:
            print("⚠ SUPABASE_URL not configured. Storage will be disabled.")
            self.supabase = None
            return
        
        if not self.storage_url:
            print("⚠ SUPABASE_STORAGE_URL not configured. Storage will be disabled.")
            self.supabase = None
            return
        
        # Initialize Supabase client with service role key for admin operations
        try:
            if self.supabase_service_role_key:
                self.supabase: Client = create_client(
                    self.supabase_url, 
                    self.supabase_service_role_key
                )
                print("✓ Supabase client initialized with service role key")
            elif self.supabase_anon_key:
                self.supabase: Client = create_client(
                    self.supabase_url, 
                    self.supabase_anon_key
                )
                print("✓ Supabase client initialized with anon key")
            else:
                print("⚠ No Supabase keys found. Storage will be disabled.")
                self.supabase = None
        except Exception as e:
            print(f"⚠ Failed to initialize Supabase client: {e}")
            self.supabase = None
    
    def is_configured(self) -> bool:
        """Check if Supabase storage is properly configured."""
        return self.supabase is not None
    
    def get_configuration_status(self) -> dict:
        """Get detailed configuration status for debugging."""
        return {
            "supabase_url": bool(self.supabase_url),
            "supabase_anon_key": bool(self.supabase_anon_key),
            "supabase_service_role_key": bool(self.supabase_service_role_key),
            "bucket_name": self.bucket_name,
            "storage_url": bool(self.storage_url),
            "client_initialized": bool(self.supabase),
            "is_configured": self.is_configured()
        }
    
    def upload_file(self, file_content: bytes, file_name: str, content_type: str, user_id: int) -> str:
        """Upload file to Supabase Storage and return the public URL."""
        if not self.supabase:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Storage service is not configured"
            )
        
        try:
            # Generate unique file path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            file_extension = file_name.split('.')[-1] if '.' in file_name else 'pdf'
            file_path = f"user_{user_id}/{timestamp}_{unique_id}.{file_extension}"
            
            print(f"Uploading file to path: {file_path}")
            
            # Upload to Supabase Storage
            response = self.supabase.storage.from_(self.bucket_name).upload(
                path=file_path,
                file=file_content,
                file_options={
                    "content-type": content_type,
                    "upsert": False
                }
            )
            
            print(f"Upload response type: {type(response)}")
            print(f"Upload response: {response}")
            
            # Check if upload was successful
            # Handle different Supabase response formats
            upload_successful = False
            error_message = None
            
            if hasattr(response, 'data') and response.data is not None:
                # Upload successful - has data
                print(f"Upload successful with data: {response.data}")
                upload_successful = True
            elif hasattr(response, 'error') and response.error is not None:
                # Upload failed - has error
                error_message = str(response.error)
                print(f"Supabase upload error: {error_message}")
            elif isinstance(response, dict):
                # Handle dict response
                if 'error' in response and response['error'] is not None:
                    error_message = str(response['error'])
                    print(f"Supabase upload error (dict): {error_message}")
                elif 'data' in response:
                    print(f"Upload successful (dict): {response['data']}")
                    upload_successful = True
                else:
                    # Assume success if no error
                    print(f"Upload response (dict, assuming success): {response}")
                    upload_successful = True
            elif response is not None:
                # Some other response format, assume success if not None
                print(f"Upload response (unknown format, assuming success): {response}")
                upload_successful = True
            else:
                error_message = "Upload returned None response"
            
            if error_message:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to upload file: {error_message}"
                )
            
            if not upload_successful:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Upload failed with unknown response format"
                )
            
            # Generate public URL
            public_url = f"{self.storage_url}/{file_path}"
            print(f"✓ File uploaded to Supabase: {public_url}")
            
            return public_url
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"Supabase upload error: {e}")
            print(f"Error type: {type(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload file to storage: {str(e)}"
            )
    
    def delete_file(self, file_url: str) -> bool:
        """Delete file from Supabase Storage."""
        if not self.supabase:
            return False
        
        try:
            # Extract file path from URL
            if self.storage_url in file_url:
                file_path = file_url.replace(f"{self.storage_url}/", "")
            else:
                print(f"Invalid file URL format: {file_url}")
                return False
            
            response = self.supabase.storage.from_(self.bucket_name).remove([file_path])
            
            print(f"Delete response: {response}")
            
            # Check if deletion was successful
            if hasattr(response, 'data') and response.data:
                print(f"✓ File deleted from Supabase: {file_path}")
                return True
            elif hasattr(response, 'error') and response.error:
                print(f"Failed to delete file: {response.error}")
                return False
            elif isinstance(response, list) and len(response) > 0:
                # Sometimes returns a list of deleted files
                print(f"✓ File deleted from Supabase: {file_path}")
                return True
            else:
                print(f"Unexpected delete response: {response}")
                return False
                
        except Exception as e:
            print(f"Supabase delete error: {e}")
            return False
    
    def generate_presigned_url(self, file_url: str, expiration: int = 3600) -> str:
        """Generate a signed URL for private file access."""
        if not self.supabase:
            return file_url
        
        try:
            # Extract file path from URL
            if self.storage_url in file_url:
                file_path = file_url.replace(f"{self.storage_url}/", "")
            else:
                return file_url  # Return original URL if format is unexpected
            
            # Create signed URL
            response = self.supabase.storage.from_(self.bucket_name).create_signed_url(
                path=file_path,
                expires_in=expiration
            )
            
            if response.get('signedURL'):
                return response['signedURL']
            else:
                print(f"Failed to create signed URL: {response}")
                return file_url
                
        except Exception as e:
            print(f"Signed URL error: {e}")
            return file_url  # Return original URL on error
    
    def get_public_url(self, file_path: str) -> str:
        """Get public URL for a file."""
        if not self.supabase:
            return ""
        
        try:
            response = self.supabase.storage.from_(self.bucket_name).get_public_url(file_path)
            return response.get('publicURL', '')
        except Exception as e:
            print(f"Public URL error: {e}")
            return ""

# Create a singleton instance
supabase_storage = SupabaseStorageService()