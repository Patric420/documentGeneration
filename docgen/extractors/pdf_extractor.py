import logging
import fitz

logger = logging.getLogger(__name__)

def extract_pdf_text(path: str) -> str:
    """Extract text from PDF file using PyMuPDF."""
    logger.info(f"Extracting text from PDF: {path}")
    try:
        doc = fitz.open(path)
        text = "\n".join(page.get_text() for page in doc)
        logger.debug(f"Successfully extracted {len(text)} characters from PDF")
        doc.close()
        return text
    except Exception as e:
        logger.error(f"Error extracting PDF text: {str(e)}", exc_info=True)
        raise
