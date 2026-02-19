#!/usr/bin/env python3
"""
Document Generation CLI - Main entry point
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict

from app import generate_document

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('docgen.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Intelligent Document Generation System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --input document.pdf --fields '{"Name": "John Doe", "Date": "2024-02-16"}'
  python main.py -i sample.docx -f fields.json
  python main.py --input contract.pdf --fields-json config.json --verbose
        """
    )
    
    parser.add_argument(
        '-i', '--input',
        required=True,
        type=str,
        help='Path to input document (PDF, DOCX, or image file)'
    )
    
    parser.add_argument(
        '-f', '--fields',
        type=str,
        help='JSON string or file path containing field values'
    )
    
    parser.add_argument(
        '-j', '--fields-json',
        type=str,
        help='JSON file path containing field values (alternative to --fields)'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='output.pdf',
        help='Output PDF file path (default: output.pdf)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging (DEBUG level)'
    )
    
    parser.add_argument(
        '--list-types',
        action='store_true',
        help='List supported document types and exit'
    )
    
    return parser.parse_args()


def load_fields(fields_arg: str, fields_json_arg: str) -> Dict[str, str]:
    """
    Load field values from arguments.
    
    Args:
        fields_arg: JSON string or file path
        fields_json_arg: JSON file path
        
    Returns:
        Dictionary of field values
        
    Raises:
        ValueError: If both arguments provided or JSON parsing fails
    """
    if fields_arg and fields_json_arg:
        raise ValueError("Cannot specify both --fields and --fields-json")
    
    if not fields_arg and not fields_json_arg:
        raise ValueError("Must specify either --fields or --fields-json")
    
    source = fields_arg or fields_json_arg
    
    # Try to parse as JSON string first
    try:
        return json.loads(source)
    except json.JSONDecodeError:
        # Try to load as file
        pass
    
    # Try to load from file
    file_path = Path(source)
    if file_path.exists():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in file {source}: {str(e)}")
        except IOError as e:
            raise ValueError(f"Error reading file {source}: {str(e)}")
    
    raise ValueError(f"Could not parse fields as JSON or find file: {source}")


def list_document_types() -> None:
    """Display supported document types."""
    from schema import DOCUMENT_SCHEMAS
    
    print("\n" + "="*60)
    print("SUPPORTED DOCUMENT TYPES")
    print("="*60)
    
    for doc_type, schema in DOCUMENT_SCHEMAS.items():
        print(f"\n{doc_type}")
        print("-" * 40)
        
        required = schema.get("required", [])
        optional = schema.get("optional", [])
        
        if required:
            print("  Required fields:")
            for field in required:
                print(f"    - {field}")
        
        if optional:
            print("  Optional fields:")
            for field in optional:
                print(f"    - {field}")
    
    print("\n" + "="*60 + "\n")


def main() -> int:
    """Main CLI entry point."""
    args = None
    try:
        args = parse_arguments()
        
        # Set logging level
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
            logger.debug("Verbose logging enabled")
        
        # Handle --list-types
        if args.list_types:
            list_document_types()
            return 0
        
        logger.info("=" * 60)
        logger.info("Document Generation System")
        logger.info("=" * 60)
        
        # Validate input file
        input_path = Path(args.input)
        if not input_path.exists():
            logger.error(f"Input file not found: {args.input}")
            print(f"Error: Input file not found: {args.input}", file=sys.stderr)
            return 1
        
        # Load field values
        logger.info(f"Loading field values...")
        try:
            fields = load_fields(args.fields, args.fields_json)
        except ValueError as e:
            logger.error(f"Error loading fields: {str(e)}")
            print(f"Error: {str(e)}", file=sys.stderr)
            return 1
        
        logger.info(f"Loaded {len(fields)} field(s)")
        
        # Generate document
        logger.info(f"Starting document generation from: {args.input}")
        doc_type, output_pdf = generate_document(str(input_path), fields)
        
        logger.info(f"Document generation completed successfully!")
        logger.info(f"  Document Type: {doc_type}")
        logger.info(f"  Output PDF: {output_pdf}")
        
        print(f"\n✓ Document generated successfully!")
        print(f"  Type: {doc_type}")
        print(f"  Output: {output_pdf}\n")
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        print("\nOperation cancelled.", file=sys.stderr)
        return 130
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        print(f"\nError: {str(e)}", file=sys.stderr)
        
        if args and not args.verbose:
            print("\nRun with --verbose to see full error details")
        
        return 1


if __name__ == '__main__':
    sys.exit(main())
