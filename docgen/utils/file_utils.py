import logging
from extractors.pdf_extractor import extract_pdf_text
from extractors.docx_extractor import extract_docx_text
from extractors.image_extractor import extract_image_text

logger = logging.getLogger(__name__)

def extract_text(path: str) -> str:
    """
    Extract text from various document formats.
    
    Supports: PDF, DOCX, PNG, JPG, JPEG
    """
    logger.info(f"Processing file: {path}")
    try:
        if path.endswith(".pdf"):
            logger.debug("File type: PDF")
            return extract_pdf_text(path)
        elif path.endswith(".docx"):
            logger.debug("File type: DOCX")
            return extract_docx_text(path)
        elif path.endswith((".png", ".jpg", ".jpeg")):
            logger.debug(f"File type: Image")
            return extract_image_text(path)
        else:
            logger.error(f"Unsupported file type for: {path}")
            raise ValueError("Unsupported file type")
    except Exception as e:
        logger.error(f"Error extracting text from {path}: {str(e)}", exc_info=True)
        raise
