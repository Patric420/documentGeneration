"""
Custom exception classes for the document generation system.
"""


class DocumentGenerationError(Exception):
    """Base exception for all document generation errors."""
    pass


class FileExtractionError(DocumentGenerationError):
    """Raised when text extraction from a file fails."""
    pass


class UnsupportedFileFormatError(FileExtractionError):
    """Raised when the file format is not supported."""
    pass


class DocumentClassificationError(DocumentGenerationError):
    """Raised when document classification fails."""
    pass


class UnsupportedDocumentTypeError(DocumentClassificationError):
    """Raised when the document type is not recognized or supported."""
    pass


class ValidationError(DocumentGenerationError):
    """Raised when input validation fails."""
    pass


class MissingRequiredFieldError(ValidationError):
    """Raised when a required field is missing."""
    
    def __init__(self, document_type: str, missing_fields: list):
        self.document_type = document_type
        self.missing_fields = missing_fields
        super().__init__(
            f"Missing required fields for {document_type}: {', '.join(missing_fields)}"
        )


class InvalidFieldFormatError(ValidationError):
    """Raised when a field has invalid format."""
    
    def __init__(self, field_name: str, expected_format: str, provided_value: str):
        self.field_name = field_name
        self.expected_format = expected_format
        self.provided_value = provided_value
        super().__init__(
            f"Field '{field_name}' has invalid format. Expected: {expected_format}, Got: {provided_value}"
        )


class TemplateError(DocumentGenerationError):
    """Raised when there's an error with the template."""
    pass


class TemplateNotFoundError(TemplateError):
    """Raised when a template file is not found."""
    pass


class LatexCompilationError(DocumentGenerationError):
    """Raised when LaTeX compilation fails."""
    pass


class APIError(DocumentGenerationError):
    """Raised when API calls fail."""
    pass


class APIRateLimitError(APIError):
    """Raised when API rate limit is exceeded."""
    pass


class APIUnavailableError(APIError):
    """Raised when API service is unavailable."""
