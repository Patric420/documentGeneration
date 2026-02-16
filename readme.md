# Document Generation System

An intelligent document generation and classification system that automatically extracts text from various document formats, classifies them using Google Gemini AI, validates required fields, and generates personalized documents from LaTeX templates.

## Features

- **Multi-format Text Extraction**: Support for PDF, DOCX, and image files (PNG, JPG, JPEG)
- **AI-Powered Document Classification**: Automatically classify documents into predefined types using Google Gemini
- **Smart Field Validation**: Validate user inputs against document-type-specific schemas
- **Template-Based Generation**: Generate documents from LaTeX templates with dynamic field replacement
- **Robust Error Handling**: Automatic retry logic for API calls with exponential backoff
- **OCR Support**: Extract text from images using Tesseract OCR

## Supported Document Types

The system can classify and generate the following document types:

1. **NDA** - Non-Disclosure Agreement
   - Required: Name, Company, Date, Term, Jurisdiction
   - Optional: Confidential_Info_Description, Governing_Law

2. **Offer_Letter** - Job Offer Letter
   - Required: Name, Company, Position, Start_Date, Salary
   - Optional: Manager_Name, Response_Date, HR_Manager, Benefits_Description

3. **Contract** - Service/Business Contract
   - Required: Client_Name, Company, Contract_Creation_Date, Service_Description, Payment_Amount, Start_Date, End_Date
   - Optional: Payment_Schedule, Termination_Clause

4. **MOU** - Memorandum of Understanding
   - Required: PartyA_Name, PartyB_Name, Date, Purpose, Term, Jurisdiction
   - Optional: Confidentiality, Termination_Clause, Governing_Law

5. **IP_Agreement** - Intellectual Property Agreement
   - Required: Name, Company, Date, Term, Jurisdiction
   - Optional: IP_Description, Governing_Law

6. **Onboarding_Letter** - Employee Onboarding Letter
   - Required: Employee_Name, Emp_ID, Role, Joining_Date, Document_Date
   - Optional: None

## Project Structure

```
docgen/
├── app.py                          # Main application logic
├── config.py                       # Configuration and environment variables
├── schema.py                       # Document schemas with required/optional fields
├── requirements.txt                # Python dependencies
├── extractors/
│   ├── pdf_extractor.py           # Extract text from PDF files (PyMuPDF)
│   ├── docx_extractor.py          # Extract text from DOCX files (python-docx)
│   └── image_extractor.py         # Extract text from images using OCR (Tesseract)
├── classifier/
│   └── classify.py                # Document classification using Google Gemini
├── generators/
│   └── generate.py                # Prompt generation for document generation
├── utils/
│   ├── file_utils.py              # Multi-format file handling and text extraction
│   ├── latex_writer.py            # LaTeX template rendering and PDF generation
│   ├── pdf_writer.py              # Alternative PDF generation using ReportLab
│   └── retry.py                   # Retry logic with exponential backoff for API calls
├── templates/
│   └── onboarding_template.tex    # LaTeX template for onboarding letters
└── images/                        # Directory for template images
```

## Installation

### Prerequisites

- Python 3.8+
- LaTeX distribution (pdflatex) - Required for PDF generation
- Tesseract OCR - Required for image text extraction

### Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

**Key Dependencies:**

- `google-genai` - Google Gemini AI API client
- `PyMuPDF` (fitz) - PDF text extraction
- `python-docx` - DOCX file handling
- `pytesseract` - OCR text extraction
- `Pillow` - Image processing
- `python-dotenv` - Environment variable management
- `reportlab` - Alternative PDF generation

### Environment Setup

Create a `.env` file in the `docgen/` directory with your Google Gemini API key:

```env
GEMINI_API_KEY=your_api_key_here
```

## Usage

### Basic Document Generation

```python
from app import generate_document

# Input file and required fields
file_path = "path/to/sample_document.pdf"
user_inputs = {
    "Employee_Name": "John Doe",
    "Emp_ID": "EMP001",
    "Role": "Senior Developer",
    "Joining_Date": "2024-03-01",
    "Document_Date": "2024-02-15"
}

# Generate document
doc_type, output_pdf = generate_document(file_path, user_inputs)
print(f"Generated {doc_type} document: {output_pdf}")
```

### Workflow

1. **Extract Text** - The system extracts text from the input document (PDF, DOCX, or image)
2. **Classify** - Google Gemini classifies the document into one of the supported types
3. **Validate** - User inputs are validated against the document-type schema
4. **Generate** - A LaTeX template is populated with user inputs and compiled to PDF

## Configuration

### config.py

- `GEMINI_API_KEY` - Google Gemini API authentication key
- `MODEL_NAME` - Currently uses `gemini-2.5-flash` (optimized for speed and cost)

### schema.py

Define document-type-specific requirements and optional fields. Each document type has:
- `required` - Fields that must be provided by the user
- `optional` - Fields that can be optionally provided

## API Reference

### Core Functions

#### `extract_text(path)` - Located in `utils/file_utils.py`
Extracts text from a document file.

**Parameters:**
- `path` (str) - Path to the document file (.pdf, .docx, .png, .jpg, .jpeg)

**Returns:**
- (str) Extracted text content

**Supported Formats:**
- PDF files using PyMuPDF
- DOCX files using python-docx
- Images (PNG, JPG, JPEG) using Tesseract OCR

---

#### `classify_document(text)` - Located in `classifier/classify.py`
Classifies document text into one of the supported document types using Google Gemini.

**Parameters:**
- `text` (str) - Document text to classify

**Returns:**
- (str) Classified document type (NDA, Offer_Letter, Contract, MOU, IP_Agreement, or Onboarding_Letter)

**Raises:**
- `ValueError` - If classification output is not a valid document type

---

#### `generate_document(file_path, user_inputs)` - Located in `app.py`
Main function for document generation workflow.

**Parameters:**
- `file_path` (str) - Path to the input document
- `user_inputs` (dict) - Dictionary of field values to populate in the template

**Returns:**
- (tuple) Containing:
  - `doc_type` (str) - Classified document type
  - `output_pdf` (str) - Path to generated PDF file

**Workflow:**
1. Extracts text from input document
2. Classifies the document
3. Validates user inputs against document schema
4. Generates LaTeX file from template
5. Compiles LaTeX to PDF

**Raises:**
- `ValueError` - If document type is unsupported or required fields are missing

---

#### `render_latex(template_path, output_tex, output_pdf, values)` - Located in `utils/latex_writer.py`
Renders a LaTeX template with user values and generates a PDF.

**Parameters:**
- `template_path` (str) - Path to LaTeX template file
- `output_tex` (str) - Output path for rendered LaTeX file
- `output_pdf` (str) - Output path for generated PDF
- `values` (dict) - Dictionary of field values to replace in template

**Note:** Uses pdflatex for compilation. Requires LaTeX distribution to be installed.

---

#### `call_gemini_with_retry(client, model, prompt, retries=5)` - Located in `utils/retry.py`
Calls Google Gemini API with automatic retry logic for handling rate limits and service unavailability.

**Parameters:**
- `client` - Google Gemini client instance
- `model` (str) - Model name (e.g., "gemini-2.5-flash")
- `prompt` (str) - Prompt text to send to the model
- `retries` (int) - Number of retry attempts (default: 5)

**Returns:**
- API response with generated content

**Behavior:**
- Detects 503 errors, UNAVAILABLE, or "overloaded" messages
- Uses exponential backoff: 2^i seconds between attempts
- Raises RuntimeError if all retries fail

## Error Handling

### Common Issues and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `ValueError: Unsupported file type` | Input file has unsupported extension | Use .pdf, .docx, or image files (.png, .jpg, .jpeg) |
| `ValueError: Missing required fields` | User didn't provide all required fields | Check schema.py for required fields for the document type |
| `ValueError: Unsupported document type` | Classifier returned invalid type | Document doesn't match any supported type; may need classifier adjustment |
| `RuntimeError: Gemini unavailable after retries` | API service temporarily down | Retry later; check API status or quota |
| `FileNotFoundError: pdflatex not found` | LaTeX not installed | Install LaTeX distribution (MiKTeX on Windows, TeX Live on Linux) |

## Extensions

### Adding a New Document Type

1. Update `schema.py` to add document type and required/optional fields
2. Create/update LaTeX template in `templates/` directory
3. Update `TEMPLATE_MAP` in `app.py` to map document type to template file
4. Optionally update classifier prompts in `classify.py` to recognize the new type

### Adding Template Images

1. Place image files in the `images/` directory
2. Reference them in LaTeX templates (paths are relative to the template directory)
3. Supported formats: PNG, JPG, PDF

## Performance Considerations

- **API Rate Limiting**: The retry logic handles Google Gemini rate limits with exponential backoff
- **OCR Processing**: Large images may take time to process - consider image resolution
- **LaTeX Compilation**: First PDF generation may be slower as LaTeX needs to set up; subsequent runs are faster
- **Batch Processing**: For high-volume document generation, consider implementing queuing

## Security Considerations

- API keys are loaded from `.env` files using `python-dotenv` - ensure `.env` is in `.gitignore`
- Template field replacement uses simple string replacement - be cautious with user inputs in production
- Validate all user inputs against schema before processing
- Consider sandboxing LaTeX compilation in production environments

## Testing

The project includes a Jupyter notebook `check.ipynb` for testing and development:

```bash
jupyter notebook check.ipynb
```

## Future Enhancements

- [ ] Support for additional document formats (RTF, ODT, etc.)
- [ ] Batch document generation API
- [ ] Web interface for document generation
- [ ] Document template editor
- [ ] Support for additional output formats (DOCX, HTML)
- [ ] Multilingual document support
- [ ] Document versioning and history tracking

## License

[Add your license information here]

## Support

For issues, feature requests, or questions, please contact the development team or create an issue in the project repository.

---

**Last Updated:** February 16, 2026
