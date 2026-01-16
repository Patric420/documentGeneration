from utils.file_utils import extract_text
from classifier.classify import classify_document
from generators.generate import build_prompt
from schema import DOCUMENT_SCHEMAS
from utils.pdf_writer import save_text_as_pdf
from utils.retry import call_gemini_with_retry
from google import genai
from config import GEMINI_API_KEY, MODEL_NAME

client = genai.Client(api_key=GEMINI_API_KEY)

def validate_inputs(doc_type, user_inputs):
    if doc_type == "Other":
        return

    schema = DOCUMENT_SCHEMAS.get(doc_type)
    if not schema:
        raise ValueError(f"Unsupported document type: {doc_type}")

    missing = [f for f in schema["required"] if f not in user_inputs or not user_inputs[f]]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")

def generate_document(file_path, user_inputs):
    extracted_text = extract_text(file_path)
    doc_type = classify_document(extracted_text)

    validate_inputs(doc_type, user_inputs)

    prompt = build_prompt(doc_type, extracted_text, user_inputs)
    response = call_gemini_with_retry(client, MODEL_NAME, prompt)

    final_text = response.text
    output_pdf = "output.pdf"
    save_text_as_pdf(final_text, output_pdf)

    return doc_type, final_text, output_pdf

if __name__ == "__main__":
    file_path = "sample.pdf"

    user_inputs = {
    "Employee_Name": "Rahul Verma",
    "Emp_ID": "T2L-AI-041",
    "Role": "Software Engineer Intern",
    "Joining_Date": "1 July 2026",
    "Document_Date": "10 June 2026"
    }


    doc_type, result, pdf_path = generate_document(file_path, user_inputs)
    print("Detected:", doc_type)
    print("Saved as:", pdf_path)
