# DocGen — Intelligent Document Generation

AI-powered system that classifies documents with Google Gemini, validates fields, and generates branded PDFs from LaTeX templates.

## Highlights

- **Multi-format extraction** — PDF, DOCX, and images (PNG / JPG via Tesseract OCR)
- **AI classification** — Gemini automatically detects the document type
- **Schema-driven validation** — required / optional fields enforced per type
- **LaTeX templating** — branded output with injection-safe field substitution
- **Streamlit dashboard** — upload, fill fields, preview the PDF, tweak and regenerate
- **Batch processing** — concurrent generation via `ThreadPoolExecutor`
- **Retry & resilience** — exponential back-off on Gemini rate limits

## Supported Document Types

| Type | Required Fields | Template |
|------|----------------|----------|
| **Onboarding Letter** | Employee_Name, Emp_ID, Role, Joining_Date, Document_Date | ✅ |
| **NDA** | Name, Company, Date, Term, Jurisdiction | 🔜 |
| **Offer Letter** | Name, Company, Position, Start_Date, Salary | 🔜 |
| **Contract** | Client_Name, Company, Contract_Creation_Date, Service_Description, Payment_Amount, Start_Date, End_Date | 🔜 |
| **MOU** | PartyA_Name, PartyB_Name, Date, Purpose, Term, Jurisdiction | 🔜 |
| **IP Agreement** | Name, Company, Date, Term, Jurisdiction | 🔜 |

## Quick Start

### Prerequisites

| Tool | Purpose |
|------|---------|
| Python 3.8+ | Runtime |
| pdflatex (MiKTeX / TeX Live) | PDF compilation |
| Tesseract OCR *(optional)* | Image text extraction |

### Install

```bash
cd docgen
pip install -r requirements.txt
```

### Configure

Create `docgen/.env`:

```env
GEMINI_API_KEY=your_key_here
```

### Run the Dashboard

```bash
cd docgen
streamlit run dashboard.py
```

The dashboard lets you:
1. **Upload** a reference document (PDF / DOCX / image)
2. **Review** the AI-detected type and fill in fields
3. **Preview** the generated PDF inline
4. **Edit** any field and click **Regenerate** to update the preview instantly
5. **Download** the final PDF

### CLI Usage

```bash
# Inline fields
python main.py -i sample.pdf -f '{"Employee_Name": "Jane", "Emp_ID": "E01", "Role": "Dev", "Joining_Date": "2026-03-01", "Document_Date": "2026-02-19"}'

# Fields from a JSON file
python main.py -i sample.pdf --fields-json fields.json

# List supported types
python main.py --list-types

# Verbose logging
python main.py -i sample.pdf -f fields.json -v
```

### Programmatic API

```python
from app import generate_document

doc_type, pdf_path = generate_document("sample.pdf", {
    "Employee_Name": "Jane Doe",
    "Emp_ID": "E01",
    "Role": "Engineer",
    "Joining_Date": "2026-03-01",
    "Document_Date": "2026-02-19",
})
```

### Batch Processing

```python
from batch_processor import BatchProcessor

processor = BatchProcessor(max_workers=4)
jobs = [("job1", "doc1.pdf", {"Name": "Alice", ...}),
        ("job2", "doc2.pdf", {"Name": "Bob",   ...})]
results = processor.process_batch(jobs)
processor.save_batch_report("report.json")
```

## Project Structure

```
docgen/
├── dashboard.py              # Streamlit web UI
├── app.py                    # Core generation pipeline
├── main.py                   # CLI entry point
├── config.py                 # Env-based configuration
├── schema.py                 # Document type schemas
├── exceptions.py             # Custom exception hierarchy
├── batch_processor.py        # Concurrent batch runner
├── test_suite.py             # Unit tests
├── classifier/
│   └── classify.py           # Gemini-based document classification
├── extractors/
│   ├── pdf_extractor.py      # PyMuPDF
│   ├── docx_extractor.py     # python-docx
│   └── image_extractor.py    # Tesseract OCR
├── generators/
│   └── generate.py           # Prompt builder for Gemini
├── utils/
│   ├── file_utils.py         # Multi-format text extraction
│   ├── latex_writer.py       # Template rendering + pdflatex
│   ├── pdf_writer.py         # ReportLab fallback
│   ├── retry.py              # Exponential back-off
│   ├── validators.py         # Field validation (email, date, etc.)
│   ├── output_manager.py     # Session-based output dirs
│   └── config_manager.py     # Multi-source config loader
├── templates/
│   └── onboarding_template.tex
└── images/                   # Template assets
```

## Configuration

All settings can be set via environment variables or a `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | — | Google Gemini API key (**required**) |
| `MODEL_NAME` | `gemini-2.5-flash` | Gemini model |
| `OUTPUT_DIR` | `generated_documents` | Output directory |
| `LOG_LEVEL` | `INFO` | Logging level |
| `API_RETRIES` | `5` | Max retry attempts |

## Error Handling

```
DocumentGenerationError
├── FileExtractionError
│   └── UnsupportedFileFormatError
├── DocumentClassificationError
│   └── UnsupportedDocumentTypeError
├── ValidationError
│   ├── MissingRequiredFieldError
│   └── InvalidFieldFormatError
├── TemplateError
│   ├── TemplateNotFoundError
│   └── LatexCompilationError
└── APIError
    ├── APIRateLimitError
    └── APIUnavailableError
```

## Adding a New Document Type

1. Add the schema to `schema.py` (required + optional fields)
2. Create a LaTeX template in `templates/`
3. Register it in `TEMPLATE_MAP` inside `app.py`
4. *(Optional)* Add field validators in `utils/validators.py`

## Development

```bash
pip install -r requirements-dev.txt
python -m pytest test_suite.py -v          # run tests
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines and [DEPLOYMENT.md](DEPLOYMENT.md) for Docker / cloud deployment.

---

**Last updated:** February 19, 2026
