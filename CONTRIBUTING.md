# Contributing Guide

Thank you for your interest in contributing to the Document Generation System! This guide will help you get started.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Documentation](#documentation)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

This project adheres to a Contributor Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Getting Started

### Prerequisites

- Python 3.8+
- Git
- Virtual environment tool (venv, virtualenv, or conda)

### Setup Development Environment

1. Fork the repository on GitHub

2. Clone your fork:
```bash
git clone https://github.com/YOUR_USERNAME/documentGeneration.git
cd documentGeneration
```

3. Add upstream remote:
```bash
git remote add upstream https://github.com/ORIGINAL_OWNER/documentGeneration.git
```

4. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

5. Install development dependencies:
```bash
pip install -r docgen/requirements.txt
pip install -r docgen/requirements-dev.txt
```

6. Install pre-commit hooks:
```bash
cd docgen && pre-commit install
```

7. Verify setup:
```bash
cd docgen && python -m pytest test_suite.py -v
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or for bug fixes:
git checkout -b fix/bug-description
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `refactor/` - Code refactoring
- `docs/` - Documentation updates
- `test/` - Testing improvements
- `perf/` - Performance improvements

### 2. Make Your Changes

Write clean, well-documented code:

```python
def process_document(input_path: str, fields: Dict[str, str]) -> Tuple[str, str]:
    """
    Process a document with the given fields.
    
    Args:
        input_path: Path to the input document
        fields: Dictionary of field values
        
    Returns:
        Tuple of (document_type, output_path)
        
    Raises:
        FileExtractionError: If document extraction fails
        DocumentGenerationError: If generation fails
    """
    logger.info(f"Processing document: {input_path}")
    # Implementation here
```

### 3. Run Tests and Checks

```bash
cd docgen

# Run all checks
make quality

# Or individually:
make test              # Run tests
make lint              # Check code style
make type-check        # Type checking
make security          # Security checks
make format            # Auto-format code
```

### 4. Commit Changes

Follow conventional commits format:

```bash
git add .
git commit -m "type(scope): description

Detailed explanation of changes if needed.
- List any breaking changes
- Reference related issues: Fixes #123"
```

Commit types:
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `style` - Code style changes (formatting)
- `refactor` - Code restructuring
- `perf` - Performance improvements
- `test` - Test additions/changes
- `chore` - Build, CI, or dependency updates

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Code Standards

### Style Guide

We follow PEP 8 with some customizations:

- Line length: 100 characters (enforced by Black)
- Imports: Sorted by isort with Black profile
- Type hints: Required for all functions

### Code Quality

- **Type Hints**: All functions must have type hints
- **Docstrings**: Document all modules, classes, and functions
- **Logging**: Use logging module instead of print()
- **Error Handling**: Use custom exceptions from `exceptions.py`
- **Testing**: Write tests for new functionality

### Example Code

```python
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Process documents with type safety and logging."""
    
    def __init__(self, output_dir: str = "output"):
        """Initialize processor."""
        self.output_dir = output_dir
        logger.info(f"Initialized processor with output: {output_dir}")
    
    def process(self, input_path: str, fields: Dict[str, str]) -> Optional[str]:
        """
        Process a document.
        
        Args:
            input_path: Path to document
            fields: Field values
            
        Returns:
            Path to output document or None if failed
        """
        try:
            logger.debug(f"Processing {input_path}")
            # Process logic here
            return "output.pdf"
        except Exception as e:
            logger.error(f"Processing failed: {str(e)}", exc_info=True)
            raise
```

## Testing

### Writing Tests

All new code should include tests. We use pytest:

```python
import pytest
from exceptions import ValidationError

class TestDocumentValidator:
    """Test document validation."""
    
    def test_valid_email(self):
        """Test email validation."""
        from utils.validators import FieldValidator
        assert FieldValidator.validate_email("user@example.com")
    
    def test_invalid_email(self):
        """Test invalid email."""
        from utils.validators import FieldValidator
        assert not FieldValidator.validate_email("invalid")
    
    def test_raises_on_missing_fields(self):
        """Test error on missing required fields."""
        with pytest.raises(ValidationError):
            # Test code that should raise
            pass
```

### Test Coverage

Aim for:
- 80%+ code coverage
- All public functions tested
- Error cases tested

Run coverage:
```bash
pytest test_suite.py --cov=. --cov-report=html
```

## Commit Guidelines

### Format

```
<type>(<scope>): <subject>
<blank line>
<body>
<blank line>
<footer>
```

### Examples

```
feat(classifier): Add support for new document type

- Add NDA_V2 document type to schema
- Update classifier to recognize new type
- Add tests for new classification

Fixes #456
```

```
fix(latex): Escape special characters in user input

Prevent LaTeX injection attacks by properly escaping
user-provided field values before template substitution.

Fixes #789
```

## Pull Request Process

### Before Submitting

1. **Update from upstream**:
   ```bash
   git fetch upstream
   git rebase upstream/develop
   ```

2. **Run all tests**:
   ```bash
   make test
   ```

3. **Fix code style**:
   ```bash
   make format
   ```

4. **Run quality checks**:
   ```bash
   make quality
   ```

### PR Template

```markdown
## Description
Brief description of changes

## Related Issues
Fixes #(issue number)

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Refactoring
- [ ] Performance improvement

## Testing Done
- [ ] Unit tests added/updated
- [ ] Tests pass locally
- [ ] Test coverage maintained

## Documentation
- [ ] README updated if needed
- [ ] Inline documentation added
- [ ] Examples provided

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] No new warnings generated
- [ ] Added tests for changes
- [ ] Updated documentation
```

### Review Process

- Maintainers will review within 5 business days
- Address feedback in new commits
- Ensure CI/CD pipelines pass
- Sign off from at least one maintainer required

## Documentation

### Code Documentation

- Every module should have a module docstring
- Every class should have a docstring
- Every function should have a docstring with Args, Returns, Raises

```python
"""Module for processing documents.

This module handles extraction, classification, and generation
of documents using various file formats and AI models.
"""

def generate_document(input_path: str, fields: dict) -> tuple:
    """
    Generate a document from a template.
    
    Args:
        input_path: Path to input document file
        fields: Dictionary of field values for template
        
    Returns:
        Tuple of (document_type, output_path)
        
    Raises:
        FileExtractionError: If file cannot be extracted
        DocumentGenerationError: If generation fails
    """
```

### Update README

If making significant changes, update the README:

1. Add new features to Features section
2. Update API reference if changing function signatures
3. Add examples for new functionality
4. Update troubleshooting section

## Reporting Issues

### Issue Template

```markdown
## Description
Clear description of the issue

## Steps to Reproduce
1. Step 1
2. Step 2
3. ...

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- Python version: 
- OS: 
- Relevant packages: `pip freeze`

## Additional Context
Any additional information
```

### Bug Report Checklist

- [ ] Searched existing issues
- [ ] Minimal reproducible example
- [ ] Full error traceback included
- [ ] Environment details provided
- [ ] Relevant configuration included

## Development Tips

### Useful Commands

```bash
# Run specific test
pytest test_suite.py::TestClass::test_method -v

# Run with debugging
pytest test_suite.py --pdb

# Run specific test pattern
pytest -k "email" -v

# Generate HTML coverage report
pytest --cov=. --cov-report=html

# Format all code
make format

# Type check
make type-check
```

### Debug Logging

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Or via environment:

```bash
LOG_LEVEL=DEBUG python main.py
```

### Performance Profiling

```python
from memory_profiler import profile

@profile
def my_function():
    # Code to profile
    pass
```

```bash
python -m memory_profiler myscript.py
```

## Getting Help

- **Discussions**: GitHub Discussions for questions
- **Issues**: GitHub Issues for bugs and features
- **Documentation**: Check README.md and DEPLOYMENT.md
- **Examples**: Review example code in docgen/

## Community

Thank you for contributing! We appreciate:
- Bug reports
- Feature suggestions
- Code improvements
- Documentation enhancements
- Test coverage improvements

Your contributions help make this project better for everyone!

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
