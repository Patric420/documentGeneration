import logging
import fitz
from exceptions import FileExtractionError

logger = logging.getLogger(__name__)

def extract_pdf_text(path: str) -> str:
    """Extract text from PDF file using PyMuPDF."""
    logger.info(f"Extracting text from PDF: {path}")
    try:
        with fitz.open(path) as doc:
            text = "\n".join(page.get_text() for page in doc)
        logger.debug(f"Successfully extracted {len(text)} characters from PDF")
        return text
    except FileExtractionError:
        raise
    except Exception as e:
        logger.error(f"Error extracting PDF text: {str(e)}", exc_info=True)
        raise FileExtractionError(f"Failed to extract text from PDF {path}: {str(e)}")
