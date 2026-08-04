"""
S3-compatible storage client (AWS S3 or MinIO).
"""
from datetime import timedelta
from typing import BinaryIO
from uuid import uuid4

import boto3
from botocore.exceptions import ClientError

from app.core.config import settings
from app.core.exceptions import FileDeleteError, FileDownloadError, FileUploadError
from app.core.logging import get_logger

logger = get_logger(__name__)


class S3Storage:
    """
    S3-compatible storage client.
    
    Architectural Decision:
    - Uses boto3 for S3 operations
    - Supports both AWS S3 and MinIO
    - Generates signed URLs for secure access
    - Organizes files by user_id for isolation
    """
    
    def __init__(self):
        self.client = boto3.client(
            's3',
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
            region_name=settings.S3_REGION,
            use_ssl=settings.S3_USE_SSL
        )
        self.bucket = settings.S3_BUCKET_NAME
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self) -> None:
        """Create bucket if it doesn't exist."""
        try:
            self.client.head_bucket(Bucket=self.bucket)
        except ClientError:
            try:
                self.client.create_bucket(Bucket=self.bucket)
                logger.info("Created S3 bucket", extra={"bucket": self.bucket})
            except Exception as e:
                logger.warning("Could not create bucket", extra={"error": str(e)})
    
    def upload_file(
        self,
        file_data: bytes | BinaryIO,
        user_id: str,
        folder: str,
        filename: str | None = None
    ) -> str:
        """
        Upload file to S3.
        
        Args:
            file_data: File bytes or file object
            user_id: User ID for organizing files
            folder: Folder name (original, processed, exports)
            filename: Optional custom filename
            
        Returns:
            S3 key (path) of uploaded file
            
        Raises:
            FileUploadError: If upload fails
        """
        try:
            if filename is None:
                filename = f"{uuid4()}.pdf"
            
            key = f"{user_id}/{folder}/{filename}"
            
            if isinstance(file_data, bytes):
                self.client.put_object(
                    Bucket=self.bucket,
                    Key=key,
                    Body=file_data,
                    ContentType='application/pdf'
                )
            else:
                self.client.upload_fileobj(
                    file_data,
                    self.bucket,
                    key,
                    ExtraArgs={'ContentType': 'application/pdf'}
                )
            
            logger.info("File uploaded", extra={"key": key, "user_id": user_id})
            return key
        
        except Exception as e:
            logger.error("File upload failed", extra={"error": str(e)})
            raise FileUploadError(f"Failed to upload file: {str(e)}")
    
    def download_file(self, key: str) -> bytes:
        """
        Download file from S3.
        
        Args:
            key: S3 key (path) of file
            
        Returns:
            File bytes
            
        Raises:
            FileDownloadError: If download fails
        """
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
            return response['Body'].read()
        
        except Exception as e:
            logger.error("File download failed", extra={"key": key, "error": str(e)})
            raise FileDownloadError(f"Failed to download file: {str(e)}")
    
    def delete_file(self, key: str) -> None:
        """
        Delete file from S3.
        
        Args:
            key: S3 key (path) of file
            
        Raises:
            FileDeleteError: If deletion fails
        """
        try:
            self.client.delete_object(Bucket=self.bucket, Key=key)
            logger.info("File deleted", extra={"key": key})
        
        except Exception as e:
            logger.error("File deletion failed", extra={"key": key, "error": str(e)})
            raise FileDeleteError(f"Failed to delete file: {str(e)}")
    
    def get_presigned_url(
        self,
        key: str,
        expires_in: int = 3600
    ) -> str:
        """
        Generate presigned URL for file access.
        
        Args:
            key: S3 key (path) of file
            expires_in: URL expiration in seconds (default 1 hour)
            
        Returns:
            Presigned URL
        """
        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': key},
                ExpiresIn=expires_in
            )
            return url
        
        except Exception as e:
            logger.error("Failed to generate presigned URL", extra={"key": key, "error": str(e)})
            return f"s3://{self.bucket}/{key}"  # Fallback
    
    def get_public_url(self, key: str) -> str:
        """
        Get public URL for file (if bucket is public).
        
        Args:
            key: S3 key (path) of file
            
        Returns:
            Public URL
        """
        if settings.S3_ENDPOINT_URL:
            # MinIO or custom endpoint
            return f"{settings.S3_ENDPOINT_URL}/{self.bucket}/{key}"
        else:
            # AWS S3
            return f"https://{self.bucket}.s3.{settings.S3_REGION}.amazonaws.com/{key}"
    
    def file_exists(self, key: str) -> bool:
        """
        Check if file exists in S3.
        
        Args:
            key: S3 key (path) of file
            
        Returns:
            True if file exists, False otherwise
        """
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError:
            return False


# Global storage instance
storage = S3Storage()
