import logging
import time
from exceptions import APIRateLimitError, APIUnavailableError

logger = logging.getLogger(__name__)

def call_gemini_with_retry(client, model: str, prompt: str, retries: int = 5):
    """
    Call Google Gemini API with automatic retry logic.
    
    Handles rate limiting and service unavailability with exponential backoff.
    
    Args:
        client: Google Gemini client instance
        model: Model name to use
        prompt: Prompt text to send
        retries: Number of retry attempts
        
    Returns:
        API response
        
    Raises:
        APIUnavailableError: If all retry attempts fail
    """
    logger.info(f"Attempting Gemini API call with max {retries} retries")
    for i in range(retries):
        try:
            logger.debug(f"API call attempt {i+1}/{retries}")
            return client.models.generate_content(
                model=model,
                contents=prompt
            )
        except Exception as e:
            msg = str(e)
            if "503" in msg or "UNAVAILABLE" in msg or "overloaded" in msg:
                wait = 2 ** i
                logger.warning(f"Model overloaded (attempt {i+1}/{retries}). Retrying in {wait}s...")
                time.sleep(wait)
            else:
                logger.error(f"Unrecoverable error during API call: {str(e)}")
                raise e
    logger.error("Gemini API unavailable after all retry attempts")
    raise APIUnavailableError("Gemini unavailable after retries")
