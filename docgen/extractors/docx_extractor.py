import logging
from docx import Document

logger = logging.getLogger(__name__)

def extract_docx_text(path: str) -> str:
    """Extract text from DOCX file."""
    logger.info(f"Extracting text from DOCX: {path}")
    try:
        doc = Document(path)
        text = "\n".join(p.text for p in doc.paragraphs)
        logger.debug(f"Successfully extracted {len(text)} characters from DOCX")
        return text
    except Exception as e:
        logger.error(f"Error extracting DOCX text: {str(e)}", exc_info=True)
        raise
