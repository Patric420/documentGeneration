"""
Input validation utilities for document generation.
"""

import logging
import re
from typing import Dict, List, Optional
from datetime import datetime
from exceptions import InvalidFieldFormatError

logger = logging.getLogger(__name__)


class FieldValidator:
    """Validates document fields against expected formats."""
    
    # Common patterns
    ISO_DATE_PATTERN = r'^\d{4}-\d{2}-\d{2}$'  # YYYY-MM-DD
    DATE_FORMAT_PATTERN = r'^\d{1,2}/\d{1,2}/\d{4}$'  # MM/DD/YYYY or M/D/YYYY
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    PHONE_PATTERN = r'^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$'
    CURRENCY_PATTERN = r'^\$?[0-9]{1,3}(,[0-9]{3})*(\.[0-9]{2})?$'
    NUMBER_PATTERN = r'^[0-9]+(\.[0-9]+)?$'
    ALPHA_PATTERN = r'^[a-zA-Z\s]+$'
    ALPHANUMERIC_PATTERN = r'^[a-zA-Z0-9\s\-_]+$'

    @staticmethod
    def validate_date(value: str, format: str = 'iso') -> bool:
        """
        Validate date format.
        
        Args:
            value: Date string to validate
            format: 'iso' (YYYY-MM-DD) or 'standard' (MM/DD/YYYY)
            
        Returns:
            True if valid, False otherwise
        """
        try:
            if format == 'iso':
                pattern = FieldValidator.ISO_DATE_PATTERN
                if not re.match(pattern, value):
                    return False
                parts = value.split('-')
                datetime(int(parts[0]), int(parts[1]), int(parts[2]))
                return True
            elif format == 'standard':
                pattern = FieldValidator.DATE_FORMAT_PATTERN
                if not re.match(pattern, value):
                    return False
                parts = value.split('/')
                month, day, year = int(parts[0]), int(parts[1]), int(parts[2])
                datetime(year, month, day)
                return True
        except (ValueError, IndexError):
            return False
        return False

    @staticmethod
    def validate_email(value: str) -> bool:
        """Validate email format."""
        return bool(re.match(FieldValidator.EMAIL_PATTERN, value.strip()))

    @staticmethod
    def validate_phone(value: str) -> bool:
        """Validate phone number format."""
        return bool(re.match(FieldValidator.PHONE_PATTERN, value.strip()))

    @staticmethod
    def validate_currency(value: str) -> bool:
        """Validate currency format."""
        return bool(re.match(FieldValidator.CURRENCY_PATTERN, value.strip()))

    @staticmethod
    def validate_number(value: str) -> bool:
        """Validate numeric format."""
        try:
            float(value.strip())
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_alpha(value: str) -> bool:
        """Validate alphabetic characters only."""
        return bool(re.match(FieldValidator.ALPHA_PATTERN, value.strip()))

    @staticmethod
    def validate_alphanumeric(value: str) -> bool:
        """Validate alphanumeric characters."""
        return bool(re.match(FieldValidator.ALPHANUMERIC_PATTERN, value.strip()))

    @staticmethod
    def validate_not_empty(value: str) -> bool:
        """Validate that field is not empty."""
        return bool(value.strip())

    @staticmethod
    def validate_length(value: str, min_length: int = 0, max_length: int = None) -> bool:
        """Validate string length."""
        length = len(value.strip())
        if length < min_length:
            return False
        if max_length and length > max_length:
            return False
        return True


class FieldValidationRule:
    """Defines validation rules for a field."""
    
    def __init__(self, field_name: str, required: bool = True, 
                 validators: Optional[List[tuple]] = None, description: str = ""):
        """
        Initialize field validation rule.
        
        Args:
            field_name: Name of the field
            required: Whether field is required
            validators: List of (validator_func, validator_name) tuples
            description: Field description for error messages
        """
        self.field_name = field_name
        self.required = required
        self.validators = validators or []
        self.description = description

    def validate(self, value: Optional[str]) -> bool:
        """Validate a value against this rule."""
        if not value:
            return not self.required
        
        for validator_func, _ in self.validators:
            if not validator_func(value):
                return False
        return True

    def get_error_message(self, value: str) -> str:
        """Get friendly error message for invalid value."""
        if not value and self.required:
            return f"'{self.field_name}' is required but empty"
        
        for validator_func, validator_name in self.validators:
            if not validator_func(value):
                return f"'{self.field_name}' has invalid {validator_name}: '{value}'"
        
        return f"'{self.field_name}' validation failed"


class DocumentValidator:
    """Validates complete documents against schema."""
    
    # Default validation rules for common fields
    DEFAULT_RULES = {
        'Name': FieldValidationRule(
            'Name',
            required=True,
            validators=[(FieldValidator.validate_not_empty, 'format'),
                       (lambda x: FieldValidator.validate_length(x, 2, 100), 'length')],
            description='Full name'
        ),
        'Date': FieldValidationRule(
            'Date',
            required=True,
            validators=[(lambda x: FieldValidator.validate_date(x, 'iso'), 'date format (YYYY-MM-DD)')],
            description='Date in ISO format'
        ),
        'Email': FieldValidationRule(
            'Email',
            required=False,
            validators=[(FieldValidator.validate_email, 'email format')],
            description='Email address'
        ),
        'Phone': FieldValidationRule(
            'Phone',
            required=False,
            validators=[(FieldValidator.validate_phone, 'phone format')],
            description='Phone number'
        ),
        'Salary': FieldValidationRule(
            'Salary',
            required=False,
            validators=[(FieldValidator.validate_currency, 'currency format') ,
                       (lambda x: FieldValidator.validate_number(x.replace('$', '').replace(',', '')), 'numeric value')],
            description='Salary in currency format'
        ),
    }

    @staticmethod
    def get_rule_for_field(field_name: str) -> Optional[FieldValidationRule]:
        """Get validation rule for a field."""
        return DocumentValidator.DEFAULT_RULES.get(field_name)

    @staticmethod
    def validate_fields(fields: Dict[str, str], required_fields: List[str]) -> Dict[str, str]:
        """
        Validate all provided fields.
        
        Args:
            fields: Dictionary of field names to values
            required_fields: List of required field names
            
        Returns:
            Dictionary of field names to validation errors (empty if all valid)
            
        Raises:
            InvalidFieldFormatError: If validation fails
        """
        errors = {}
        logger.info(f"Validating {len(fields)} fields")
        
        # Get validation rules for each field
        for field_name, value in fields.items():
            rule = DocumentValidator.get_rule_for_field(field_name)
            
            if rule and not rule.validate(value):
                error_msg = rule.get_error_message(value)
                errors[field_name] = error_msg
                logger.error(f"Validation failed for '{field_name}': {error_msg}")
        
        # Check required fields are present
        for field_name in required_fields:
            if field_name not in fields or not fields[field_name].strip():
                error_msg = f"Required field '{field_name}' is missing"
                errors[field_name] = error_msg
                logger.error(error_msg)
        
        if errors:
            logger.error(f"Validation errors found: {errors}")
            # Raise the first error found
            first_error_field = list(errors.keys())[0]
            raise InvalidFieldFormatError(
                first_error_field,
                "valid format",
                fields.get(first_error_field, "")
            )
        
        logger.info("All fields validated successfully")
        return errors
