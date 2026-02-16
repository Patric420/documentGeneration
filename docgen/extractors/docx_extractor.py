import logging
from docx import Document
from exceptions import FileExtractionError

logger = logging.getLogger(__name__)

def extract_docx_text(path: str) -> str:
    """Extract text from DOCX file."""
    logger.info(f"Extracting text from DOCX: {path}")
    try:
        doc = Document(path)
        text = "\n".join(p.text for p in doc.paragraphs)
        logger.debug(f"Successfully extracted {len(text)} characters from DOCX")
        return text
    except FileExtractionError:
        raise
    except Exception as e:
        logger.error(f"Error extracting DOCX text: {str(e)}", exc_info=True)
        raise FileExtractionError(f"Failed to extract text from DOCX {path}: {str(e)}")
