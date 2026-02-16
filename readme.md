# Document Generation System

An intelligent document generation and classification system that automatically extracts text from various document formats, classifies them using Google Gemini AI, validates required fields, and generates personalized documents from LaTeX templates.

## Features

### Core Features
- **Multi-format Text Extraction**: Support for PDF, DOCX, and image files (PNG, JPG, JPEG)
- **AI-Powered Document Classification**: Automatically classify documents into predefined types using Google Gemini
- **Smart Field Validation**: Validate user inputs against document-type-specific schemas using regex patterns
- **Template-Based Generation**: Generate documents from LaTeX templates with dynamic field replacement
- **Robust Error Handling**: Custom exception hierarchy with granular error handling and automatic retry logic
- **OCR Support**: Extract text from images using Tesseract OCR
- **LaTeX Injection Prevention**: Built-in sanitization of special LaTeX characters in user inputs

### Advanced Features
- **Batch Processing**: Process multiple documents concurrently with ThreadPoolExecutor
- **Session Management**: Organized output with session-based directory structure and metadata tracking
- **Configuration Management**: Load configuration from .env files, JSON, or environment variables
- **CLI Interface**: Command-line entry point with multiple options for flexibility
- **Comprehensive Logging**: Configurable logging with rotating file handlers and multiple log levels
- **Type Hints**: Full type annotations throughout the codebase for better IDE support and error detection
- **Input Validation**: Flexible validation system with regex validators for common field types
- **CI/CD Pipelines**: GitHub Actions workflows for testing and code quality checks

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
├── app.py                          # Main application logic with type hints and exceptions
├── main.py                         # CLI entry point with command-line arguments
├── config.py                       # Configuration and environment variables
├── schema.py                       # Document schemas with required/optional fields
├── exceptions.py                   # Custom exception hierarchy (14 classes)
├── batch_processor.py              # Batch processing with concurrent execution
├── test_suite.py                   # Comprehensive unit tests (45+ tests)
├── logging_config.json             # Logging configuration with rotating handlers
├── requirements.txt                # Python dependencies (pinned versions)
├── requirements-dev.txt            # Development dependencies (testing, linting, etc.)
├── setup_dev_env.py                # Development environment setup script
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
│   ├── latex_writer.py            # LaTeX template rendering with security fixes
│   ├── pdf_writer.py              # Alternative PDF generation using ReportLab
│   ├── retry.py                   # Retry logic with exponential backoff for API calls
│   ├── validators.py              # Input validation with regex patterns
│   ├── output_manager.py          # Session-based output organization
│   └── config_manager.py          # Configuration management from multiple sources
├── templates/
│   └── onboarding_template.tex    # LaTeX template for onboarding letters
├── images/                        # Directory for template images
├── .env.example                   # Environment variables template
├── .pre-commit-config.yaml        # Pre-commit hooks configuration
├── Makefile                       # Build automation with 20+ targets
├── DEPLOYMENT.md                  # Deployment guides for Docker, AWS, GCP, Azure
└── CONTRIBUTING.md                # Contribution guidelines and development workflow
```

## Installation

### Prerequisites

- Python 3.8+
- LaTeX distribution (pdflatex) - Required for PDF generation
- Tesseract OCR - Required for image text extraction

### Standard Installation

Install the required Python packages:

```bash
cd docgen
pip install -r requirements.txt
```

**Key Dependencies:**
- `google-genai` - Google Gemini AI API client
- `PyMuPDF` - PDF text extraction
- `python-docx` - DOCX file handling
- `pytesseract` - OCR text extraction
- `Pillow` - Image processing
- `python-dotenv` - Environment variable management
- `reportlab` - Alternative PDF generation

### Development Installation

For development with testing, linting, and code quality tools:

```bash
cd docgen
pip install -r requirements.txt
pip install -r requirements-dev.txt
pre-commit install
python setup_dev_env.py
```

**Development Dependencies Include:**
- `pytest` - Testing framework
- `black`, `isort`, `flake8`, `mypy` - Code quality tools
- `pylint`, `bandit` - Linting and security scanning
- `sphinx` - Documentation generation

### Environment Setup

Create a `.env` file in the `docgen/` directory (use `.env.example` as template):

```env
GEMINI_API_KEY=your_api_key_here
MODEL_NAME=gemini-2.5-flash
OUTPUT_DIR=output
LOG_LEVEL=INFO
LOG_FILE=docgen.log
API_RETRIES=5
LATEX_TIMEOUT_SECONDS=30
ENABLE_VALIDATION=true
CLEANUP_OLD_SESSIONS_DAYS=30
```

All configuration values have sensible defaults and can be overridden via environment variables.

## Usage

### Interactive Mode (Recommended)

The easiest way to generate documents is using interactive mode - just run the app and answer prompts:

```bash
cd docgen
python app.py
```

The system will:
1. Ask you for the input document path
2. Extract and automatically classify the document
3. Prompt for all required fields (with validation)
4. Optionally ask for any additional fields
5. Generate and save the PDF

**Example session:**
```
============================================================
Document Generation System - Interactive Mode
============================================================

Enter path to input document (PDF/DOCX/Image): sample.pdf

Processing document...
✓ Document classified as: Onboarding_Letter

============================================================
Document Type: Onboarding_Letter
============================================================

REQUIRED FIELDS:
------------------------------------------------------------
Enter Employee_Name: John Doe
Enter Emp_ID: EMP001
Enter Role: Senior Developer
Enter Joining_Date: 2024-03-01
Enter Document_Date: 2024-02-15

OPTIONAL FIELDS:
------------------------------------------------------------
Enter Designation (leave blank to skip): 
Enter Manager (leave blank to skip): Jane Smith

Generating document...

============================================================
✓ SUCCESS
============================================================
Document Type: Onboarding_Letter
Output File: output.pdf
============================================================
```

### CLI Interface (Programmatic)

For scripting and automation, use the `main.py` CLI interface:

```bash
python main.py --input document.pdf --fields '{"Name": "John Doe", "Company": "ABC Corp"}'
```

**Command Options:**
- `--input PATH` - Path to input document (required)
- `--fields JSON` - Field values as JSON string
- `--fields-json PATH` - Path to JSON file with field values
- `--list-types` - List all supported document types
- `--verbose` - Enable verbose logging output

**Examples:**

```bash
# Generate with inline fields
python main.py --input sample.pdf --fields '{"Employee_Name": "Jane Smith", "Emp_ID": "EMP002"}'

# Generate with JSON file
python main.py --input sample.pdf --fields-json fields.json

# List supported document types
python main.py --list-types

# Verbose output for debugging
python main.py --input sample.pdf --fields-json fields.json --verbose
```

### Programmatic API

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

### Interactive Input Helper Functions

Use these functions to build interactive workflows:

```python
from app import get_input_file_interactively, get_user_inputs_interactive

# Interactively get file path (with validation)
file_path = get_input_file_interactively()

# Interactively get user fields based on document type
doc_type = "Onboarding_Letter"
user_inputs = get_user_inputs_interactive(doc_type)

# Then generate the document
from app import generate_document
doc_type, output_pdf = generate_document(file_path, user_inputs)
```

### Batch Processing

Process multiple documents concurrently:

```python
from batch_processor import BatchProcessor, BatchJob

processor = BatchProcessor(max_workers=4)

# Create batch jobs
jobs = [
    BatchJob(input_path="doc1.pdf", fields={"Name": "John", "Company": "ABC"}),
    BatchJob(input_path="doc2.pdf", fields={"Name": "Jane", "Company": "XYZ"}),
    BatchJob(input_path="doc3.pdf", fields={"Name": "Bob", "Company": "DEF"}),
]

# Process batch
results = processor.process_batch(jobs)

# Get summary
summary = processor.get_batch_summary()
print(f"Total: {summary['total']}, Success: {summary['success']}, Failed: {summary['failed']}")

# Save report
processor.save_batch_report("batch_report.json")
```

Load and process batch from JSON file:

```python
from batch_processor import BatchProcessor

processor = BatchProcessor()
batch_data = processor.load_batch_from_json("batch_jobs.json")
results = processor.process_batch(batch_data['jobs'])
```

### Validation

Validate input fields before processing:

```python
from utils.validators import DocumentValidator

# Use built-in validators
validator = DocumentValidator()
errors = validator.validate({"email": "invalid-email", "phone": "123"})
if errors:
    print(f"Validation errors: {errors}")

# Custom validation
from utils.validators import FieldValidator
is_valid = FieldValidator.validate_email("user@example.com")
print(f"Email valid: {is_valid}")
```

## Configuration

### ConfigurationManager

Configuration can be loaded from multiple sources with precedence order:
1. `.env.local` file (highest priority)
2. `.env` file
3. `config.json` file
4. Environment variables
5. Default values (lowest priority)

```python
from utils.config_manager import get_config

# Get configuration (automatically loads from .env, JSON, env vars)
config = get_config()

# Access settings
api_key = config.gemini_api_key
model = config.model_name
output_dir = config.output_dir
```

### Configuration Keys

- `GEMINI_API_KEY` - Google Gemini API authentication key
- `MODEL_NAME` - AI model to use (default: `gemini-2.5-flash`)
- `OUTPUT_DIR` - Directory for generated documents (default: `output`)
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR) (default: `INFO`)
- `LOG_FILE` - Log file path (default: `docgen.log`)
- `API_RETRIES` - Number of API retry attempts (default: `5`)
- `LATEX_TIMEOUT_SECONDS` - LaTeX compilation timeout (default: `30`)
- `ENABLE_VALIDATION` - Enable input validation (default: `true`)
- `CLEANUP_OLD_SESSIONS_DAYS` - Auto-cleanup session age threshold (default: `30`)

## API Reference

### Exception Classes (exceptions.py)

The system uses a custom exception hierarchy for granular error handling:

**Hierarchy:**
```
DocumentGenerationError (base)
├── FileExtractionError
├── DocumentClassificationError
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

**Usage:**
```python
from exceptions import ValidationError, MissingRequiredFieldError, FileExtractionError

try:
    # Some operation
    pass
except MissingRequiredFieldError as e:
    print(f"Missing field: {e}")
except FileExtractionError as e:
    print(f"Could not extract file: {e}")
```

### Validators (utils/validators.py)

Input validation with regex patterns:

```python
from utils.validators import FieldValidator, DocumentValidator

# Validate individual fields
FieldValidator.validate_email("user@example.com")      # Returns: bool
FieldValidator.validate_phone("+1-555-0123")           # Returns: bool
FieldValidator.validate_currency("$1,000.50")          # Returns: bool
FieldValidator.validate_date("2024-03-15")             # Returns: bool

# Validate entire document
validator = DocumentValidator()
errors = validator.validate({
    "email": "invalid",
    "phone": "123",
    "name": ""
})
# Returns: {"email": "Invalid email format", "phone": "Invalid phone..."}
```

**Supported Validators:**
- Email addresses
- Phone numbers (US format)
- Currency (US format)
- ISO dates (YYYY-MM-DD)
- Numbers (integers and decimals)
- Alphabetic characters
- Alphanumeric characters
- String length

### OutputManager (utils/output_manager.py)

Session-based output organization with metadata tracking:

```python
from utils.output_manager import OutputManager

manager = OutputManager(base_output_dir="output")

# Get session directory
session_dir = manager.get_session_dir()

# Save generated document
doc_path = manager.save_generated_document(
    doc_type="Onboarding_Letter",
    filename="output.pdf",
    source_file="input.pdf"
)

# Track metadata
manager.save_metadata({
    "document_type": "Onboarding_Letter",
    "fields_used": ["Employee_Name", "Emp_ID"],
    "generated_at": "2024-02-16T10:30:00"
})

# Clean old sessions (>30 days)
manager.cleanup_old_sessions(days=30)

# List all sessions
sessions = manager.list_sessions()
```

### ConfigurationManager (utils/config_manager.py)

Multi-source configuration management:

```python
from utils.config_manager import get_config, ConfigurationManager

# Get global configuration instance
config = get_config()
api_key = config.gemini_api_key

# Initialize with custom config file
ConfigurationManager.init_config(config_file="custom_config.json")

# Convert to dictionary (masks sensitive values)
config_dict = config.to_dict()
```

### BatchProcessor (batch_processor.py)

Concurrent batch document processing:

```python
from batch_processor import BatchProcessor, BatchJob

processor = BatchProcessor(max_workers=4, session_name="batch_001")

# Create jobs
jobs = [
    BatchJob(input_path="doc1.pdf", fields={"Name": "John"}),
    BatchJob(input_path="doc2.pdf", fields={"Name": "Jane"}),
]

# Process concurrently
results = processor.process_batch(jobs)

# Get status
status = processor.get_job_status(job_id)

# Save report
processor.save_batch_report("report.json")

# Load batch from JSON
batch_data = processor.load_batch_from_json("batch.json")
```

### Interactive Input Functions (app.py)

#### `get_input_file_interactively()` 
Prompts user for input file path with file existence validation.

**Returns:**
- (str) Path to validated input file

**Behavior:**
- Loops until user provides a valid file path
- Validates file exists on filesystem
- Strips whitespace from input
- Logs file selection

**Example:**
```python
from app import get_input_file_interactively
file_path = get_input_file_interactively()
# Output: Enter path to input document (PDF/DOCX/Image): sample.pdf
```

---

#### `get_user_inputs_interactive(doc_type)`
Interactively prompts user for document-type-specific required and optional fields.

**Parameters:**
- `doc_type` (str) - Document type to collect fields for

**Returns:**
- (dict) Dictionary of field values provided by user

**Behavior:**
- Displays document type and field sections
- Required fields: loops until value provided
- Optional fields: allows skipping (enter blank)
- Validates input against schema
- Pretty-printed output with separators
- Logs all user inputs

**Example:**
```python
from app import get_user_inputs_interactive
fields = get_user_inputs_interactive("Onboarding_Letter")
# Prompts for: Employee_Name, Emp_ID, Role, Joining_Date, Document_Date
# Optionally: Designation, Manager, etc.
```

---

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

### Exception Hierarchy

The system uses a comprehensive custom exception hierarchy for precise error handling:

```python
from exceptions import (
    DocumentGenerationError,
    FileExtractionError,
    DocumentClassificationError,
    ValidationError,
    MissingRequiredFieldError,
    InvalidFieldFormatError,
    TemplateNotFoundError,
    LatexCompilationError,
    APIRateLimitError,
    APIUnavailableError
)

try:
    doc_type, output = generate_document("input.pdf", fields)
except MissingRequiredFieldError as e:
    print(f"Missing field: {e}")
    # Handle missing field
except InvalidFieldFormatError as e:
    print(f"Invalid format: {e}")
    # Handle format validation
except FileExtractionError as e:
    print(f"Cannot extract file: {e}")
    # Provide different file or format
except APIUnavailableError as e:
    print(f"API temporarily unavailable: {e}")
    # Retry later
except LatexCompilationError as e:
    print(f"LaTeX compilation failed: {e}")
    # Check LaTeX installation
except DocumentGenerationError as e:
    print(f"General error: {e}")
    # Fallback handling
```

### Common Issues and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `FileExtractionError` | Input file cannot be extracted | Ensure file is valid PDF, DOCX, or image (.png, .jpg, .jpeg) |
| `MissingRequiredFieldError` | Required field not provided | Check schema.py for required fields; pass all required values |
| `InvalidFieldFormatError` | Field fails validation | Use correct format (email, phone, currency format, ISO date) |
| `DocumentClassificationError` | Document type unrecognizable | Document doesn't match any supported type; review document |
| `TemplateNotFoundError` | LaTeX template missing | Ensure template exists in docgen/templates/ directory |
| `LatexCompilationError` | LaTeX compilation fails | Install LaTeX distribution (MiKTeX/TeX Live/MacTeX); check template syntax |
| `APIRateLimitError` | Gemini API rate limited | Retry after backoff; reduce concurrent requests |
| `APIUnavailableError` | Gemini API temporarily down | Retry later; check API status; verify API key quotas |

## Performance Considerations

- **API Rate Limiting**: Automatic retry logic with exponential backoff handles API rate limits
- **Concurrent Processing**: ThreadPoolExecutor-based batch processing for parallel document generation
- **OCR Processing**: Large images may take time - consider image resolution and preprocessing
- **LaTeX Compilation**: First PDF generation slower as LaTeX initializes; subsequent runs faster
- **Session Management**: Automatic cleanup of old sessions (configurable retention period)
- **Connection Pooling**: Reuse API connections for better performance in batch operations

## Security Considerations

- **LaTeX Injection Prevention**: All user inputs sanitized before template substitution
- **API Key Protection**: Load from `.env` files (never hardcode); ensure `.env` in `.gitignore`
- **Input Validation**: All user inputs validated against schemas before processing
- **Exception Safety**: No sensitive information exposed in error messages
- **Type Safety**: Full type hints enable static analysis and IDE checking
- **Dependency Pinning**: All dependency versions pinned for reproducible builds
- **Code Quality**: Regular security scanning with bandit during CI/CD

## Extensions

### Adding a New Document Type

1. Update `schema.py` to add document type and required/optional fields
2. Create/update LaTeX template in `templates/` directory
3. Update `TEMPLATE_MAP` in `app.py` to map document type to template file
4. Add validation rules in `utils/validators.py` if new field types needed

### Adding Custom Validators

```python
# In utils/validators.py
class FieldValidator:
    @staticmethod
    def validate_custom_field(value: str) -> bool:
        """Validate custom field format."""
        return bool(re.match(r'^YOUR_PATTERN$', value))

# Update DEFAULT_RULES
DEFAULT_RULES = {
    'custom_field': FieldValidationRule('custom_field', 'custom')
}
```

### Adding Template Images

1. Place image files in `docgen/images/` directory
2. Reference in LaTeX templates with relative paths
3. Supported formats: PNG, JPG, PDF

## Future Enhancements

### Short-term (Planned)
- [ ] REST API server (Flask/FastAPI)
- [ ] WebSocket support for real-time generation status
- [ ] API rate limiting middleware
- [ ] Request/Job queuing with Redis/RabbitMQ

### Medium-term (Proposed)
- [ ] Web interface dashboard for document generation
- [ ] Database integration for job history and audit logs
- [ ] Authentication and role-based access control
- [ ] Prometheus metrics and monitoring
- [ ] Docker Compose setup for multi-service deployment
- [ ] Distributed tracing with correlation IDs

### Long-term (Backlog)
- [ ] Support for additional document formats (RTF, ODT)
- [ ] Web-based template editor with preview
- [ ] Support for additional output formats (DOCX, HTML)
- [ ] Multilingual document support with auto-translation
- [ ] Document versioning and change tracking
- [ ] Webhook notifications on document completion
- [ ] S3/GCS storage backend integration
- [ ] Mobile app support

## Development

### Testing

Run the comprehensive test suite:

```bash
cd docgen
make test              # Run all tests
make test-verbose      # Run with verbose output
make test-coverage     # Generate coverage report
```

**Test Coverage Includes:**
- Input validation patterns
- Output manager session management
- Configuration loading from multiple sources
- Batch processor concurrent execution
- Custom exception hierarchy
- 45+ unit tests with pytest

### Code Quality

Maintain code quality with automated checks:

```bash
cd docgen
make lint              # Run linting checks
make format            # Auto-format code with Black
make type-check        # Type checking with mypy
make security          # Security scanning with bandit
make quality           # Run all checks
```

**Tools Used:**
- **Black** - Code formatting (line length: 100)
- **isort** - Import organization
- **flake8** - Code style checking
- **mypy** - Static type checking
- **pylint** - Code quality analysis
- **bandit** - Security scanning
- **pre-commit** - Git hooks for automatic checks

### Making Changes

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes and run tests: `make quality && make test`
3. Commit with conventional message: `git commit -m "feat: description"`
4. Push and create pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## Deployment

The project includes comprehensive deployment documentation:

- **Docker**: Containerized deployment with multi-stage builds
- **systemd**: Linux service deployment with auto-restart
- **AWS Lambda**: Serverless deployment with Lambda deployment
- **Google Cloud**: Cloud Run and Compute Engine deployment
- **Azure**: Container Instances and App Service deployment
- **Monitoring**: Logging, health checks, and performance monitoring
- **Security**: Best practices, secrets management, rate limiting

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment guides.

### Quick Docker Setup

```bash
# Build image
docker build -t docgen:latest .

# Run container
docker run -e GEMINI_API_KEY=your_key docgen:latest

# With volume mount
docker run -v $(pwd)/output:/app/output docgen:latest
```

### Build Automation

Use the Makefile for common tasks:

```bash
make help              # Show all available targets
make install           # Install dependencies
make install-dev       # Install with dev dependencies
make setup             # Setup development environment
make test              # Run tests
make format            # Format code
make clean             # Remove build artifacts
make docs              # Generate documentation
make run               # Run the application
```

## License

[Add your license information here]

## Support

For issues, feature requests, or questions, please contact the development team or create an issue in the project repository.

---

**Last Updated:** February 16, 2026
