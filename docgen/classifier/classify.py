import logging
from google import genai
from config import GEMINI_API_KEY, MODEL_NAME
from utils.retry import call_gemini_with_retry

logger = logging.getLogger(__name__)

client = genai.Client(api_key=GEMINI_API_KEY)
ALLOWED_TYPES = (
    "NDA",
    "Offer_Letter",
    "Contract",
    "MOU",
    "IP_Agreement",
    "Onboarding_Letter",
)


def _normalize_doc_type(raw_text: str) -> str:
    """Normalize and validate document type classification."""
    logger.debug(f"Normalizing document type: {raw_text}")
    candidate = (raw_text or "").strip()
    if candidate in ALLOWED_TYPES:
        logger.debug(f"Valid document type found: {candidate}")
        return candidate

    candidate_lower = candidate.lower()
    for doc_type in ALLOWED_TYPES:
        if doc_type.lower() in candidate_lower:
            logger.debug(f"Fuzzy matched document type: {doc_type}")
            return doc_type

    logger.error(f"Unsupported classification output: {candidate!r}")
    raise ValueError(f"Unsupported classification output: {candidate!r}")

def classify_document(text: str) -> str:
    """
    Classify a document using Google Gemini AI.
    
    Args:
        text: Input document text to classify
        
    Returns:
        Classified document type
        
    Raises:
        ValueError: If classification output is invalid
    """
    logger.info("Calling Gemini API for document classification")
    prompt = f"""
Classify this document into exactly one of:
{", ".join(ALLOWED_TYPES)}.

Do NOT return Other.
Choose the closest match.
Return only the label.

Document:
{text[:3000]}
"""
    try:
        response = call_gemini_with_retry(client, MODEL_NAME, prompt)
        doc_type = _normalize_doc_type(response.text)
        logger.info(f"Document successfully classified as: {doc_type}")
        return doc_type
    except Exception as e:
        logger.error(f"Error during classification: {str(e)}", exc_info=True)
        raise
