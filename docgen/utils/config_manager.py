"""
Configuration management for the document generation system.
Supports environment variables, .env files, and config files.
"""

import logging
import os
import json
from pathlib import Path
from typing import Any, Dict, Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class ConfigurationManager:
    """Manages application configuration from multiple sources."""
    
    DEFAULT_CONFIG_FILE = ".docgen.config"
    DEFAULT_ENV_FILE = ".env"
    
    # Default configuration values
    DEFAULT_CONFIG = {
        'gemini_api_key': None,
        'model_name': 'gemini-2.5-flash',
        'output_dir': 'generated_documents',
        'log_level': 'INFO',
        'log_file': 'docgen.log',
        'max_log_size_mb': 10,
        'backup_logs': 3,
        'cleanup_old_sessions_days': 7,
        'enable_validation': True,
        'latex_timeout_seconds': 60,
        'api_retries': 5,
        'api_retry_backoff_base': 2,
    }
    
    def __init__(self, config_file: str = None, env_file: str = None):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Path to config file (JSON or .env format)
            env_file: Path to .env file
        """
        self.config: Dict[str, Any] = self.DEFAULT_CONFIG.copy()
        logger.info("Initializing configuration manager")
        
        # Load from env file
        if env_file:
            self._load_env_file(env_file)
        elif Path(self.DEFAULT_ENV_FILE).exists():
            self._load_env_file(self.DEFAULT_ENV_FILE)
        else:
            load_dotenv()
        
        # Load from config file
        if config_file:
            self._load_config_file(config_file)
        elif Path(self.DEFAULT_CONFIG_FILE).exists():
            self._load_config_file(self.DEFAULT_CONFIG_FILE)
        
        # Load from environment variables (takes precedence)
        self._load_from_env()
        
        logger.info("Configuration loaded successfully")
    
    def _load_env_file(self, filepath: str) -> None:
        """Load configuration from .env file."""
        env_path = Path(filepath)
        if env_path.exists():
            logger.debug(f"Loading environment from: {filepath}")
            load_dotenv(filepath)
        else:
            logger.warning(f"Environment file not found: {filepath}")
    
    def _load_config_file(self, filepath: str) -> None:
        """Load configuration from JSON or config file."""
        config_path = Path(filepath)
        
        if not config_path.exists():
            logger.warning(f"Config file not found: {filepath}")
            return
        
        try:
            logger.debug(f"Loading configuration from: {filepath}")
            with open(config_path, 'r', encoding='utf-8') as f:
                if filepath.endswith('.json'):
                    file_config = json.load(f)
                else:
                    # Parse simple key=value format
                    file_config = {}
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            if '=' in line:
                                key, value = line.split('=', 1)
                                file_config[key.strip()] = value.strip()
            
            # Merge with existing config
            self.config.update(file_config)
            logger.info(f"Loaded {len(file_config)} config values from file")
        except Exception as e:
            logger.error(f"Error loading config file: {str(e)}")
            raise
    
    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        env_mapping = {
            'GEMINI_API_KEY': 'gemini_api_key',
            'MODEL_NAME': 'model_name',
            'OUTPUT_DIR': 'output_dir',
            'LOG_LEVEL': 'log_level',
            'LOG_FILE': 'log_file',
            'API_RETRIES': 'api_retries',
        }
        
        for env_var, config_key in env_mapping.items():
            value = os.getenv(env_var)
            if value:
                logger.debug(f"Loading {config_key} from environment variable {env_var}")
                self.config[config_key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        value = self.config.get(key, default)
        logger.debug(f"Config.get('{key}') = {value}")
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        logger.debug(f"Setting config['{key}'] = {value}")
        self.config[key] = value
    
    def validate(self) -> bool:
        """
        Validate critical configuration settings.
        
        Returns:
            True if valid, False otherwise
        """
        logger.info("Validating configuration")
        
        # Check required fields
        if not self.get('gemini_api_key'):
            logger.warning("GEMINI_API_KEY not configured")
            return False
        
        # Validate numeric settings
        try:
            int(self.get('api_retries'))
            int(self.get('max_log_size_mb'))
        except (TypeError, ValueError) as e:
            logger.error(f"Invalid numeric configuration: {str(e)}")
            return False
        
        logger.info("Configuration validation passed")
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Get all configuration as dictionary.
        
        Returns:
            Configuration dictionary (API key masked)
        """
        config_copy = self.config.copy()
        if 'gemini_api_key' in config_copy and config_copy['gemini_api_key']:
            config_copy['gemini_api_key'] = '***' + config_copy['gemini_api_key'][-4:]
        return config_copy
    
    def save_config(self, filepath: str, format: str = 'json') -> None:
        """
        Save current configuration to file.
        
        Args:
            filepath: Path to save config file
            format: 'json' or 'env'
        """
        try:
            config_to_save = self.config.copy()
            
            if format == 'json':
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(config_to_save, f, indent=2)
            elif format == 'env':
                with open(filepath, 'w', encoding='utf-8') as f:
                    for key, value in config_to_save.items():
                        f.write(f"{key.upper()}={value}\n")
            
            logger.info(f"Configuration saved to: {filepath}")
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
            raise


# Global configuration instance
_global_config: Optional[ConfigurationManager] = None


def get_config() -> ConfigurationManager:
    """Get or initialize global configuration."""
    global _global_config
    if _global_config is None:
        _global_config = ConfigurationManager()
    return _global_config


def init_config(config_file: str = None, env_file: str = None) -> ConfigurationManager:
    """Initialize global configuration with specific files."""
    global _global_config
    _global_config = ConfigurationManager(config_file, env_file)
    return _global_config
