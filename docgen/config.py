import logging
from dotenv import load_dotenv
import os

logger = logging.getLogger(__name__)

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY environment variable not set")

MODEL_NAME = "gemini-2.5-flash"
logger.debug(f"Using model: {MODEL_NAME}")
