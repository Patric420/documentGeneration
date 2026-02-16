import logging
import pytesseract
from PIL import Image
from exceptions import FileExtractionError

logger = logging.getLogger(__name__)

def extract_image_text(path: str) -> str:
    """Extract text from image file using OCR."""
    logger.info(f"Extracting text from image: {path}")
    try:
        text = pytesseract.image_to_string(Image.open(path))
        logger.debug(f"Successfully extracted {len(text)} characters from image")
        return text
    except FileExtractionError:
        raise
    except Exception as e:
        logger.error(f"Error extracting image text: {str(e)}", exc_info=True)
        raise FileExtractionError(f"Failed to extract text from image {path}: {str(e)}")
