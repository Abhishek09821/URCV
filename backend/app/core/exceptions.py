"""
Custom application exceptions.
All business logic exceptions are defined here for consistent error handling.
"""
from typing import Any


class URCVException(Exception):
    """Base exception for all URCV custom exceptions."""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: dict[str, Any] | None = None
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


# Authentication & Authorization Exceptions

class AuthenticationError(URCVException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed", details: dict[str, Any] | None = None):
        super().__init__(message=message, status_code=401, details=details)


class InvalidCredentialsError(AuthenticationError):
    """Raised when credentials are invalid."""
    
    def __init__(self, message: str = "Invalid email or password"):
        super().__init__(message=message)


class TokenExpiredError(AuthenticationError):
    """Raised when JWT token has expired."""
    
    def __init__(self, message: str = "Token has expired"):
        super().__init__(message=message)


class InvalidTokenError(AuthenticationError):
    """Raised when JWT token is invalid."""
    
    def __init__(self, message: str = "Invalid token"):
        super().__init__(message=message)


class AuthorizationError(URCVException):
    """Raised when user lacks permission."""
    
    def __init__(self, message: str = "Insufficient permissions", details: dict[str, Any] | None = None):
        super().__init__(message=message, status_code=403, details=details)


class InactiveUserError(AuthorizationError):
    """Raised when user account is inactive."""
    
    def __init__(self, message: str = "User account is inactive"):
        super().__init__(message=message)


# Resource Exceptions

class ResourceNotFoundError(URCVException):
    """Raised when a requested resource is not found."""
    
    def __init__(self, resource: str, identifier: str | None = None):
        message = f"{resource} not found"
        if identifier:
            message += f": {identifier}"
        super().__init__(message=message, status_code=404)


class ResourceAlreadyExistsError(URCVException):
    """Raised when attempting to create a duplicate resource."""
    
    def __init__(self, resource: str, identifier: str | None = None):
        message = f"{resource} already exists"
        if identifier:
            message += f": {identifier}"
        super().__init__(message=message, status_code=409)


# Validation Exceptions

class ValidationError(URCVException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: str | None = None, details: dict[str, Any] | None = None):
        if field:
            details = details or {}
            details["field"] = field
        super().__init__(message=message, status_code=422, details=details)


class InvalidFileError(ValidationError):
    """Raised when uploaded file is invalid."""
    
    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message=message, details=details)


class FileTooLargeError(InvalidFileError):
    """Raised when uploaded file exceeds size limit."""
    
    def __init__(self, max_size: int):
        super().__init__(
            message=f"File size exceeds maximum allowed size of {max_size} bytes",
            details={"max_size": max_size}
        )


class InvalidFileTypeError(InvalidFileError):
    """Raised when uploaded file type is not allowed."""
    
    def __init__(self, file_type: str, allowed_types: list[str]):
        super().__init__(
            message=f"File type '{file_type}' is not allowed",
            details={"file_type": file_type, "allowed_types": allowed_types}
        )


# Resume Processing Exceptions

class ResumeParsingError(URCVException):
    """Raised when resume parsing fails."""
    
    def __init__(self, message: str = "Failed to parse resume", details: dict[str, Any] | None = None):
        super().__init__(message=message, status_code=422, details=details)


class PDFExtractionError(ResumeParsingError):
    """Raised when PDF text extraction fails."""
    
    def __init__(self, message: str = "Failed to extract text from PDF"):
        super().__init__(message=message)


class OCRError(ResumeParsingError):
    """Raised when OCR processing fails."""
    
    def __init__(self, message: str = "Failed to perform OCR on PDF"):
        super().__init__(message=message)


class ResumeValidationError(URCVException):
    """Raised when resume data validation fails."""
    
    def __init__(self, message: str, validation_errors: list[dict[str, Any]] | None = None):
        details = {"validation_errors": validation_errors} if validation_errors else None
        super().__init__(message=message, status_code=422, details=details)


# Template Exceptions

class TemplateNotFoundError(ResourceNotFoundError):
    """Raised when template is not found."""
    
    def __init__(self, template_id: str):
        super().__init__(resource="Template", identifier=template_id)


class TemplateRenderError(URCVException):
    """Raised when template rendering fails."""
    
    def __init__(self, message: str = "Failed to render template", details: dict[str, Any] | None = None):
        super().__init__(message=message, status_code=500, details=details)


class ContentOverflowError(URCVException):
    """Raised when content exceeds template capacity."""
    
    def __init__(
        self,
        section: str,
        current_size: int,
        max_size: int,
        details: dict[str, Any] | None = None
    ):
        message = f"Content overflow in section '{section}': {current_size} > {max_size}"
        overflow_details = {
            "section": section,
            "current_size": current_size,
            "max_size": max_size,
            "overflow": current_size - max_size
        }
        if details:
            overflow_details.update(details)
        super().__init__(message=message, status_code=422, details=overflow_details)


# Export Exceptions

class ExportError(URCVException):
    """Raised when export generation fails."""
    
    def __init__(self, message: str = "Failed to generate export", details: dict[str, Any] | None = None):
        super().__init__(message=message, status_code=500, details=details)


class PDFGenerationError(ExportError):
    """Raised when PDF generation fails."""
    
    def __init__(self, message: str = "Failed to generate PDF"):
        super().__init__(message=message)


class DOCXGenerationError(ExportError):
    """Raised when DOCX generation fails."""
    
    def __init__(self, message: str = "Failed to generate DOCX"):
        super().__init__(message=message)


# Storage Exceptions

class StorageError(URCVException):
    """Raised when storage operation fails."""
    
    def __init__(self, message: str = "Storage operation failed", details: dict[str, Any] | None = None):
        super().__init__(message=message, status_code=500, details=details)


class FileUploadError(StorageError):
    """Raised when file upload fails."""
    
    def __init__(self, message: str = "Failed to upload file"):
        super().__init__(message=message)


class FileDownloadError(StorageError):
    """Raised when file download fails."""
    
    def __init__(self, message: str = "Failed to download file"):
        super().__init__(message=message)


class FileDeleteError(StorageError):
    """Raised when file deletion fails."""
    
    def __init__(self, message: str = "Failed to delete file"):
        super().__init__(message=message)


# AI Service Exceptions

class AIServiceError(URCVException):
    """Raised when AI service call fails."""
    
    def __init__(self, message: str = "AI service error", details: dict[str, Any] | None = None):
        super().__init__(message=message, status_code=500, details=details)


class AIQuotaExceededError(AIServiceError):
    """Raised when AI service quota is exceeded."""
    
    def __init__(self, message: str = "AI service quota exceeded"):
        super().__init__(message=message)


class AIResponseError(AIServiceError):
    """Raised when AI service returns invalid response."""
    
    def __init__(self, message: str = "Invalid AI service response"):
        super().__init__(message=message)


# Rate Limiting

class RateLimitExceededError(URCVException):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, retry_after: int | None = None):
        message = "Rate limit exceeded"
        details = {}
        if retry_after:
            message += f". Retry after {retry_after} seconds"
            details["retry_after"] = retry_after
        super().__init__(message=message, status_code=429, details=details)


# Database Exceptions

class DatabaseError(URCVException):
    """Raised when database operation fails."""
    
    def __init__(self, message: str = "Database operation failed", details: dict[str, Any] | None = None):
        super().__init__(message=message, status_code=500, details=details)


class DatabaseConnectionError(DatabaseError):
    """Raised when database connection fails."""
    
    def __init__(self, message: str = "Failed to connect to database"):
        super().__init__(message=message)
