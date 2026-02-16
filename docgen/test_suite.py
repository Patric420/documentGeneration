"""
Unit tests for the document generation system.
"""

import unittest
from pathlib import Path
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock

from utils.validators import FieldValidator, FieldValidationRule, DocumentValidator
from utils.output_manager import OutputManager
from utils.config_manager import ConfigurationManager
from exceptions import (
    InvalidFieldFormatError,
    UnsupportedFileFormatError,
    UnsupportedDocumentTypeError,
    MissingRequiredFieldError,
)


class TestFieldValidator(unittest.TestCase):
    """Tests for field validation."""
    
    def test_validate_email_valid(self):
        """Test valid email validation."""
        self.assertTrue(FieldValidator.validate_email("user@example.com"))
        self.assertTrue(FieldValidator.validate_email("test.user+tag@domain.co.uk"))
    
    def test_validate_email_invalid(self):
        """Test invalid email validation."""
        self.assertFalse(FieldValidator.validate_email("invalid@"))
        self.assertFalse(FieldValidator.validate_email("no-at-sign.com"))
        self.assertFalse(FieldValidator.validate_email("@example.com"))
    
    def test_validate_date_iso_valid(self):
        """Test valid ISO date validation."""
        self.assertTrue(FieldValidator.validate_date("2024-02-16", format='iso'))
        self.assertTrue(FieldValidator.validate_date("2000-01-01", format='iso'))
    
    def test_validate_date_iso_invalid(self):
        """Test invalid ISO date validation."""
        self.assertFalse(FieldValidator.validate_date("2024-13-01", format='iso'))
        self.assertFalse(FieldValidator.validate_date("2024-02-30", format='iso'))
        self.assertFalse(FieldValidator.validate_date("24-02-16", format='iso'))
    
    def test_validate_date_standard_valid(self):
        """Test valid standard date validation."""
        self.assertTrue(FieldValidator.validate_date("02/16/2024", format='standard'))
        self.assertTrue(FieldValidator.validate_date("1/1/2000", format='standard'))
    
    def test_validate_phone_valid(self):
        """Test valid phone validation."""
        self.assertTrue(FieldValidator.validate_phone("123-456-7890"))
        self.assertTrue(FieldValidator.validate_phone("+1(123)456-7890"))
        self.assertTrue(FieldValidator.validate_phone("123.456.7890"))
    
    def test_validate_currency_valid(self):
        """Test valid currency validation."""
        self.assertTrue(FieldValidator.validate_currency("$100.00"))
        self.assertTrue(FieldValidator.validate_currency("1,000.50"))
        self.assertTrue(FieldValidator.validate_currency("50000"))
    
    def test_validate_number_valid(self):
        """Test valid number validation."""
        self.assertTrue(FieldValidator.validate_number("123"))
        self.assertTrue(FieldValidator.validate_number("123.45"))
        self.assertTrue(FieldValidator.validate_number("-100.5"))
    
    def test_validate_number_invalid(self):
        """Test invalid number validation."""
        self.assertFalse(FieldValidator.validate_number("abc"))
        self.assertFalse(FieldValidator.validate_number("123.45.67"))
    
    def test_validate_length(self):
        """Test length validation."""
        self.assertTrue(FieldValidator.validate_length("hello", 1, 10))
        self.assertFalse(FieldValidator.validate_length("hello", 10, 20))
        self.assertFalse(FieldValidator.validate_length("hi", 3, 10))


class TestFieldValidationRule(unittest.TestCase):
    """Tests for field validation rules."""
    
    def test_rule_required_field(self):
        """Test required field validation."""
        rule = FieldValidationRule('Name', required=True)
        self.assertFalse(rule.validate(""))
        self.assertTrue(rule.validate("John Doe"))
    
    def test_rule_optional_field(self):
        """Test optional field validation."""
        rule = FieldValidationRule('Notes', required=False)
        self.assertTrue(rule.validate(""))
        self.assertTrue(rule.validate("Some notes"))
    
    def test_rule_with_validators(self):
        """Test rule with multiple validators."""
        rule = FieldValidationRule(
            'Email',
            required=True,
            validators=[
                (FieldValidator.validate_email, 'email format'),
                (FieldValidator.validate_not_empty, 'not empty')
            ]
        )
        self.assertFalse(rule.validate("invalid-email"))
        self.assertTrue(rule.validate("user@example.com"))


class TestDocumentValidator(unittest.TestCase):
    """Tests for document validation."""
    
    def test_validate_fields_valid(self):
        """Test validation with valid fields."""
        fields = {
            'Name': 'John Doe',
            'Email': 'john@example.com'
        }
        required = ['Name']
        
        errors = DocumentValidator.validate_fields(fields, required)
        self.assertEqual(errors, {})
    
    def test_validate_fields_missing_required(self):
        """Test validation with missing required fields."""
        fields = {'Email': 'john@example.com'}
        required = ['Name']
        
        with self.assertRaises(InvalidFieldFormatError):
            DocumentValidator.validate_fields(fields, required)
    
    def test_get_rule_for_field(self):
        """Test getting validation rule for field."""
        rule = DocumentValidator.get_rule_for_field('Email')
        self.assertIsNotNone(rule)
        self.assertEqual(rule.field_name, 'Email')
        
        rule = DocumentValidator.get_rule_for_field('UnknownField')
        self.assertIsNone(rule)


class TestOutputManager(unittest.TestCase):
    """Tests for output management."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = OutputManager(self.temp_dir)
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test output manager initialization."""
        self.assertTrue(Path(self.temp_dir).exists())
    
    def test_get_session_dir(self):
        """Test session directory creation."""
        session_dir = self.manager.get_session_dir()
        self.assertTrue(session_dir.exists())
        self.assertIn("session_", session_dir.name)
    
    def test_get_document_dir(self):
        """Test document directory creation."""
        session_dir = self.manager.get_session_dir()
        doc_dir = self.manager.get_document_dir("NDA", session_dir)
        self.assertTrue(doc_dir.exists())
        self.assertEqual(doc_dir.name, "NDA")
    
    def test_save_metadata(self):
        """Test metadata saving."""
        session_dir = self.manager.get_session_dir()
        metadata = {'count': 1, 'type': 'NDA'}
        
        metadata_file = self.manager.save_metadata(session_dir, metadata)
        self.assertTrue(metadata_file.exists())
        
        # Verify saved data
        with open(metadata_file, 'r') as f:
            saved_data = json.load(f)
            self.assertEqual(saved_data['count'], 1)
            self.assertEqual(saved_data['type'], 'NDA')
    
    def test_list_sessions(self):
        """Test listing sessions."""
        # Create multiple sessions
        self.manager.get_session_dir()
        self.manager.get_session_dir()
        
        sessions = self.manager.list_sessions()
        self.assertGreaterEqual(len(sessions), 2)
    
    def test_get_session_summary(self):
        """Test getting session summary."""
        session_dir = self.manager.get_session_dir()
        summary = self.manager.get_session_summary(session_dir)
        
        self.assertIn('path', summary)
        self.assertIn('created', summary)
        self.assertIn('documents', summary)


class TestConfigurationManager(unittest.TestCase):
    """Tests for configuration management."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_initialization_defaults(self):
        """Test initialization with defaults."""
        config = ConfigurationManager()
        self.assertIsNotNone(config.get('model_name'))
        self.assertEqual(config.get('api_retries'), 5)
    
    def test_get_set_config(self):
        """Test getting and setting configuration."""
        config = ConfigurationManager()
        
        config.set('custom_key', 'custom_value')
        self.assertEqual(config.get('custom_key'), 'custom_value')
    
    def test_get_with_default(self):
        """Test getting config with default."""
        config = ConfigurationManager()
        value = config.get('nonexistent_key', 'default_value')
        self.assertEqual(value, 'default_value')
    
    def test_load_json_config(self):
        """Test loading JSON configuration file."""
        config_file = Path(self.temp_dir) / 'config.json'
        config_data = {'test_key': 'test_value', 'api_retries': 3}
        
        with open(config_file, 'w') as f:
            json.dump(config_data, f)
        
        config = ConfigurationManager(str(config_file))
        self.assertEqual(config.get('test_key'), 'test_value')
        self.assertEqual(config.get('api_retries'), 3)
    
    def test_save_config_json(self):
        """Test saving configuration as JSON."""
        config = ConfigurationManager()
        config.set('test_key', 'test_value')
        
        output_file = Path(self.temp_dir) / 'saved_config.json'
        config.save_config(str(output_file), format='json')
        
        self.assertTrue(output_file.exists())
        
        with open(output_file, 'r') as f:
            saved_data = json.load(f)
            self.assertEqual(saved_data['test_key'], 'test_value')
    
    def test_to_dict_masks_api_key(self):
        """Test that API key is masked in dict representation."""
        config = ConfigurationManager()
        config.set('gemini_api_key', 'secret_api_key_12345')
        
        config_dict = config.to_dict()
        self.assertIn('***', config_dict['gemini_api_key'])
        self.assertNotIn('secret_api_key', config_dict['gemini_api_key'])


class TestExceptions(unittest.TestCase):
    """Tests for custom exceptions."""
    
    def test_missing_required_field_error(self):
        """Test MissingRequiredFieldError."""
        error = MissingRequiredFieldError('NDA', ['Name', 'Date'])
        self.assertEqual(error.document_type, 'NDA')
        self.assertEqual(error.missing_fields, ['Name', 'Date'])
        self.assertIn('NDA', str(error))
    
    def test_invalid_field_format_error(self):
        """Test InvalidFieldFormatError."""
        error = InvalidFieldFormatError('Email', 'email format', 'invalid-email')
        self.assertEqual(error.field_name, 'Email')
        self.assertIn('invalid-email', str(error))


def run_tests():
    """Run all tests."""
    unittest.main(argv=[''], exit=False, verbosity=2)


if __name__ == '__main__':
    run_tests()
