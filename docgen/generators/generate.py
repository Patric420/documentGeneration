import logging
from typing import Dict
from schema import DOCUMENT_SCHEMAS

logger = logging.getLogger(__name__)

def build_prompt(doc_type: str, extracted_text: str, user_inputs: Dict[str, str]) -> str:
    """
    Build a prompt for document generation using Gemini AI.
    
    Args:
        doc_type: Type of document to generate
        extracted_text: Reference document text
        user_inputs: User-provided field values
        
    Returns:
        Formatted prompt for Gemini AI
    """
    logger.info(f"Building generation prompt for {doc_type}")
    fields = "\n".join(f"{k}: {v}" for k, v in user_inputs.items())

    return f"""
You are generating a company owned template of {doc_type.replace('_',' ')}.

Reference document:
{extracted_text}

Use these inputs:
{fields}

STRICT RULES:
- Do NOT change any company-related text.
- Do NOT change company name, mission, address, platform, services, or signatory.
- ONLY replace employee-specific fields.
- Keep same length, structure, and formatting.
- Do NOT rewrite or summarize.
"""
