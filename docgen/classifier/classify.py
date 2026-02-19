import logging
from google import genai
from config import GEMINI_API_KEY, MODEL_NAME
from utils.retry import call_gemini_with_retry
from exceptions import UnsupportedDocumentTypeError, DocumentClassificationError

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
    raise UnsupportedDocumentTypeError(f"Classification output '{candidate}' is not a valid document type. Supported types: {', '.join(ALLOWED_TYPES)}")

def extract_fields(text: str, doc_type: str, fields: list[str]) -> dict[str, str]:
    """
    Use Gemini AI to extract field values from document text.

    Args:
        text: The (possibly user-edited) extracted text.
        doc_type: The document type (used for context in the prompt).
        fields: List of field names to extract.

    Returns:
        Dictionary mapping field names to extracted values (empty string if
        a field could not be found).
    """
    import json as _json

    if not fields:
        return {}

    logger.info(f"Extracting {len(fields)} fields for {doc_type} via Gemini")
    fields_list = ", ".join(fields)
    prompt = (
        f"You are a precise data-extraction assistant.\n"
        f"Document type: {doc_type}\n\n"
        f"Extract the following fields from the document text below:\n"
        f"{fields_list}\n\n"
        f"Return ONLY a valid JSON object mapping each field name to its "
        f"extracted value (use an empty string if the value is not found).\n"
        f"Do NOT include any explanation or markdown fencing.\n\n"
        f"Document text:\n{text[:4000]}"
    )

    try:
        response = call_gemini_with_retry(client, MODEL_NAME, prompt)
        raw = response.text.strip()
        # Strip markdown code fences if the model wraps the JSON
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1]  # drop opening fence line
            raw = raw.rsplit("```", 1)[0]  # drop closing fence
        extracted: dict = _json.loads(raw)
        # Keep only requested fields and ensure strings
        result = {f: str(extracted.get(f, "")) for f in fields}
        logger.info(f"Extracted fields: {list(result.keys())}")
        return result
    except Exception as e:
        logger.warning(f"Field extraction failed, returning empty values: {e}")
        return {f: "" for f in fields}


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
    except UnsupportedDocumentTypeError:
        raise
    except Exception as e:
        logger.error(f"Error during classification: {str(e)}", exc_info=True)
        raise DocumentClassificationError(f"Failed to classify document: {str(e)}")
