import logging
from typing import Dict, Tuple
import json
from utils.file_utils import extract_text
from classifier.classify import classify_document
from schema import DOCUMENT_SCHEMAS
from utils.latex_writer import render_latex
from exceptions import TemplateNotFoundError, ValidationError

logger = logging.getLogger(__name__)

TEMPLATE_MAP = {
    "Onboarding_Letter": "templates/onboarding_template.tex"
}

def get_user_inputs_interactive(doc_type: str) -> Dict[str, str]:
    """
    Interactively prompt user for fields required by document type.
    
    Args:
        doc_type: Document type to get inputs for
        
    Returns:
        Dictionary of field values provided by user
    """
    logger.info(f"Collecting user inputs for document type: {doc_type}")
    schema = DOCUMENT_SCHEMAS.get(doc_type)
    
    if not schema:
        logger.error(f"Unsupported document type: {doc_type}")
        raise ValidationError(f"Unsupported document type: {doc_type}")
    
    user_inputs = {}
    
    print(f"\n{'='*60}")
    print(f"Document Type: {doc_type}")
    print(f"{'='*60}\n")
    
    # Collect required fields
    print("REQUIRED FIELDS:")
    print("-" * 60)
    for field in schema.get("required", []):
        while True:
            value = input(f"Enter {field}: ").strip()
            if value:
                user_inputs[field] = value
                logger.debug(f"User provided {field}: {value}")
                break
            else:
                print(f"  ⚠️  {field} is required. Please enter a value.")
    
    # Collect optional fields
    optional_fields = schema.get("optional", [])
    if optional_fields:
        print("\nOPTIONAL FIELDS:")
        print("-" * 60)
        for field in optional_fields:
            value = input(f"Enter {field} (leave blank to skip): ").strip()
            if value:
                user_inputs[field] = value
                logger.debug(f"User provided optional {field}: {value}")
    
    print()
    return user_inputs

def get_input_file_interactively() -> str:
    """
    Interactively prompt user for input file path.
    
    Returns:
        Path to the input file
    """
    import os
    while True:
        file_path = input("Enter path to input document (PDF/DOCX/Image): ").strip()
        if not file_path:
            print("  ⚠️  File path cannot be empty.")
            continue
        if not os.path.exists(file_path):
            print(f"  ⚠️  File not found: {file_path}")
            continue
        logger.debug(f"User provided file: {file_path}")
        return file_path

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
    import sys
    
    print("\n" + "="*60)
    print("Document Generation System - Interactive Mode")
    print("="*60)
    
    try:
        # Get input file
        file_path = get_input_file_interactively()
        
        # Extract and classify
        print("\nProcessing document...")
        extracted_text = extract_text(file_path)
        doc_type = classify_document(extracted_text)
        print(f"✓ Document classified as: {doc_type}")
        
        # Get user inputs
        user_inputs = get_user_inputs_interactive(doc_type)
        
        # Generate document
        print("Generating document...")
        doc_type, pdf_path = generate_document(file_path, user_inputs)
        
        print("\n" + "="*60)
        print("✓ SUCCESS")
        print("="*60)
        print(f"Document Type: {doc_type}")
        print(f"Output File: {pdf_path}")
        print("="*60 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        logger.error(f"Application error: {str(e)}", exc_info=True)
        sys.exit(1)
