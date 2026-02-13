from utils.file_utils import extract_text
from classifier.classify import classify_document
from schema import DOCUMENT_SCHEMAS
from utils.latex_writer import render_latex

TEMPLATE_MAP = {
    "Onboarding_Letter": "templates/onboarding_template.tex"
}

def validate_inputs(doc_type, user_inputs):
    schema = DOCUMENT_SCHEMAS.get(doc_type)
    if not schema:
        raise ValueError(f"Unsupported document type: {doc_type}")

    missing = [
        f for f in schema["required"]
        if f not in user_inputs or not user_inputs[f]
    ]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")

def generate_document(file_path, user_inputs):
    # Extract text only for classification
    extracted_text = extract_text(file_path)

    # Detect document type
    doc_type = classify_document(extracted_text)

    # Validate inputs
    validate_inputs(doc_type, user_inputs)

    # Select LaTeX template
    template_path = TEMPLATE_MAP.get(doc_type)
    if not template_path:
        raise ValueError(f"No template found for {doc_type}")

    output_tex = "output.tex"
    output_pdf = "output.pdf"

    # Render PDF via LaTeX
    render_latex(
        template_path,
        output_tex,
        output_pdf,
        user_inputs
    )

    return doc_type, output_pdf


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
