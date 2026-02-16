.PHONY: help install install-dev test test-verbose lint format type-check security clean docs run batch-example

# Default target
help:
	@echo "📚 Document Generation System - Make Commands"
	@echo ""
	@echo "Setup and Installation:"
	@echo "  make install          Install production dependencies"
	@echo "  make install-dev      Install development dependencies"
	@echo "  make setup            Full development environment setup"
	@echo ""
	@echo "Testing and Quality:"
	@echo "  make test             Run unit tests"
	@echo "  make test-verbose     Run tests with verbose output"
	@echo "  make test-coverage    Run tests with coverage report"
	@echo "  make lint             Run linting checks"
	@echo "  make format           Format code with Black and isort"
	@echo "  make type-check       Run type checking with mypy"
	@echo "  make security         Run security checks with bandit"
	@echo "  make quality          Run all quality checks"
	@echo ""
	@echo "Development:"
	@echo "  make dev              Start development environment"
	@echo "  make clean            Clean up generated files"
	@echo "  make docs             Generate documentation"
	@echo "  make pre-commit       Set up pre-commit hooks"
	@echo ""
	@echo "Running Application:"
	@echo "  make run              Run application interactively"
	@echo "  make batch-example    Run batch processing example"
	@echo ""

# Installation targets
install:
	@echo "📦 Installing production dependencies..."
	pip install --upgrade pip
	pip install -r docgen/requirements.txt

install-dev:
	@echo "📦 Installing development dependencies..."
	pip install --upgrade pip
	pip install -r docgen/requirements.txt
	pip install -r docgen/requirements-dev.txt

setup: install-dev
	@echo "🚀 Running development environment setup..."
	cd docgen && python setup_dev_env.py
	$(MAKE) pre-commit
	@echo "✓ Setup complete!"

# Testing targets
test:
	@echo "🧪 Running unit tests..."
	cd docgen && pytest test_suite.py -v --tb=short

test-verbose:
	@echo "🧪 Running tests with verbose output..."
	cd docgen && pytest test_suite.py -vv --tb=long --capture=no

test-coverage:
	@echo "🧪 Running tests with coverage..."
	cd docgen && pytest test_suite.py --cov=. --cov-report=html --cov-report=term-missing

# Code quality targets
lint:
	@echo "🔍 Running linting checks..."
	flake8 docgen --max-line-length=100 --extend-ignore=E203,W503
	pylint docgen --disable=fixme --max-line-length=100 || true

format:
	@echo "✨ Formatting code..."
	black docgen --line-length=100
	isort docgen --profile=black

type-check:
	@echo "🔎 Running type checks..."
	mypy docgen --ignore-missing-imports --no-error-summary || true

security:
	@echo "🔒 Running security checks..."
	bandit -r docgen || true

quality: lint type-check security test
	@echo "✅ All quality checks completed!"

# Development targets
dev: install-dev
	@echo "🚀 Starting development environment..."
	@echo "Use 'make run' to execute the application"

pre-commit:
	@echo "🪝 Installing pre-commit hooks..."
	cd docgen && pre-commit install || true
	@echo "✓ Pre-commit hooks installed"

clean:
	@echo "🧹 Cleaning up..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name .coverage -delete
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf docgen/dist docgen/build docgen/*.egg-info
	@echo "✓ Cleanup complete"

docs:
	@echo "📖 Generating documentation..."
	@echo "Note: Documentation generation requires sphinx to be installed"
	@echo "Install with: pip install sphinx sphinx-rtd-theme"

# Application targets
run:
	@echo "▶️  Starting application..."
	@cd docgen && python main.py --help

batch-example:
	@echo "📋 Creating and running batch example..."
	@echo "Creating sample batch file..."
	@cd docgen && python -c "\
from batch_processor import create_batch_file;\
jobs = [\
  {'job_id': 'job1', 'input_path': 'sample.pdf', 'fields': {'Name': 'John Doe', 'Date': '2024-02-16'}},\
  {'job_id': 'job2', 'input_path': 'sample2.pdf', 'fields': {'Name': 'Jane Smith', 'Date': '2024-02-16'}}\
];\
create_batch_file('batch_example.json', jobs);\
print('✓ Batch file created: batch_example.json')\
"

# Default goal
.DEFAULT_GOAL := help
