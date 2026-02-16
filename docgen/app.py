import logging
from typing import Dict, Tuple
from utils.file_utils import extract_text
from classifier.classify import classify_document
from schema import DOCUMENT_SCHEMAS
from utils.latex_writer import render_latex
from exceptions import TemplateNotFoundError, ValidationError

logger = logging.getLogger(__name__)

TEMPLATE_MAP = {
    "Onboarding_Letter": "templates/onboarding_template.tex"
}

def validate_inputs(doc_type: str, user_inputs: Dict[str, str]) -> None:
    """Validate user inputs against document schema."""
    logger.info(f"Validating inputs for document type: {doc_type}")
    from exceptions import MissingRequiredFieldError
    schema = DOCUMENT_SCHEMAS.get(doc_type)
    if not schema:
        logger.error(f"Unsupported document type: {doc_type}")
        raise ValidationError(f"Unsupported document type: {doc_type}")

    missing = [
        f for f in schema["required"]
        if f not in user_inputs or not user_inputs[f]
    ]
    if missing:
        logger.error(f"Missing required fields for {doc_type}: {missing}")
        raise MissingRequiredFieldError(doc_type, missing)
    logger.debug(f"Input validation passed for {doc_type}")

def generate_document(file_path: str, user_inputs: Dict[str, str]) -> Tuple[str, str]:
    """
    Generate a document from a template based on extracted and classified input.
    
    Args:
        file_path: Path to input document (PDF, DOCX, or image)
        user_inputs: Dictionary of field values for template population
        
    Returns:
        Tuple of (document_type, output_pdf_path)
    """
    logger.info(f"Starting document generation from file: {file_path}")
    try:
        # Extract text only for classification
        logger.debug("Extracting text from input document")
        extracted_text = extract_text(file_path)
        logger.debug(f"Extracted {len(extracted_text)} characters")

        # Detect document type
        logger.info("Classifying document using Gemini AI")
        doc_type = classify_document(extracted_text)
        logger.info(f"Document classified as: {doc_type}")

        # Validate inputs
        validate_inputs(doc_type, user_inputs)

        # Select LaTeX template
        template_path = TEMPLATE_MAP.get(doc_type)
        if not template_path:
            logger.error(f"No template found for document type: {doc_type}")
            raise TemplateNotFoundError(f"No template found for document type: {doc_type}")

        output_tex = "output.tex"
        output_pdf = "output.pdf"

        logger.info(f"Rendering LaTeX template: {template_path}")
        # Render PDF via LaTeX
        render_latex(
            template_path,
            output_tex,
            output_pdf,
            user_inputs
        )
        
        logger.info(f"Successfully generated document: {output_pdf}")
        return doc_type, output_pdf
    except Exception as e:
        logger.error(f"Error during document generation: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    file_path = "sample.pdf"

    user_inputs = {
        "Employee_Name": "Rahul Verma",
        "Emp_ID": "T2L-AI-041",
        "Role": "Software Engineer Intern",
        "Joining_Date": "1 July 2026",
        "Document_Date": "10 June 2026"
    }

    doc_type, pdf_path = generate_document(file_path, user_inputs)
    print("Detected:", doc_type)
    print("Saved as:", pdf_path)
