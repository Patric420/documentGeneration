from google import genai
from config import GEMINI_API_KEY, MODEL_NAME
from utils.retry import call_gemini_with_retry

client = genai.Client(api_key=GEMINI_API_KEY)

def classify_document(text):
    prompt = f"""
Classify this document into exactly one of:
NDA, Offer_Letter, Contract, MOU, IP_Agreement, Onboarding_Letter.

Do NOT return Other.
Choose the closest match.

Document:
{text[:3000]}
"""
    response = call_gemini_with_retry(client, MODEL_NAME, prompt)
    return response.text.strip()
