import logging
from extractors.pdf_extractor import extract_pdf_text
from extractors.docx_extractor import extract_docx_text
from extractors.image_extractor import extract_image_text
from exceptions import UnsupportedFileFormatError, FileExtractionError

logger = logging.getLogger(__name__)

def extract_text(path: str) -> str:
    """
    Extract text from various document formats.
    
    Supports: PDF, DOCX, PNG, JPG, JPEG
    
    Raises:
        UnsupportedFileFormatError: If file format is not supported
        FileExtractionError: If extraction fails
    """
    logger.info(f"Processing file: {path}")
    ext = path.lower().rsplit('.', 1)[-1] if '.' in path else ''
    try:
        if ext == "pdf":
            logger.debug("File type: PDF")
            return extract_pdf_text(path)
        elif ext == "docx":
            logger.debug("File type: DOCX")
            return extract_docx_text(path)
        elif ext in ("png", "jpg", "jpeg"):
            logger.debug(f"File type: Image")
            return extract_image_text(path)
        else:
            logger.error(f"Unsupported file type for: {path}")
            raise UnsupportedFileFormatError(
                f"File format not supported: {path}. Supported formats: PDF, DOCX, PNG, JPG, JPEG"
            )
    except (UnsupportedFileFormatError, FileExtractionError):
        raise
    except Exception as e:
        logger.error(f"Error extracting text from {path}: {str(e)}", exc_info=True)
        raise FileExtractionError(f"Failed to extract text from {path}: {str(e)}")
