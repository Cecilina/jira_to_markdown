"""
Configuration management for JIRA to Markdown converter.
"""

import os
import yaml
from dotenv import load_dotenv
from typing import Dict, Any, Optional


class ConfigurationError(Exception):
    """Raised when there are configuration errors."""
    pass


class Config:
    """Configuration manager that loads and validates settings."""

    def __init__(self, config_file: Optional[str] = None, load_env: bool = True):
        """
        Initialize configuration.

        Args:
            config_file: Path to YAML config file (optional)
            load_env: Whether to load .env file
        """
        self._config = {}

        # Load environment variables from .env file
        if load_env:
            load_dotenv()

        # Load YAML config if provided
        if config_file and os.path.exists(config_file):
            self._load_yaml(config_file)
        else:
            # Set defaults
            self._set_defaults()

        # Override with environment variables
        self._load_env_overrides()

        # Validate required settings
        self._validate()

    def _load_yaml(self, config_file: str):
        """Load configuration from YAML file."""
        try:
            with open(config_file, 'r') as f:
                self._config = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Error parsing YAML config: {e}")
        except Exception as e:
            raise ConfigurationError(f"Error loading config file: {e}")

    def _set_defaults(self):
        """Set default configuration values."""
        self._config = {
            'jira': {
                'url': '',
                'username': '',
                'api_token': '',
                'verify_ssl': True
            },
            'query': {
                'jql': 'project = PROJ ORDER BY created DESC',
                'max_results': 100,
                'fields': '*all'
            },
            'output': {
                'directory': './output',
                'filename_format': '{key}.md',
                'overwrite': False
            },
            'markdown': {
                'include_metadata_table': True,
                'include_comments': True,
                'include_attachments': True,
                'include_subtasks': True,
                'include_links': True,
                'date_format': '%Y-%m-%d %H:%M:%S',
                'convert_markup': True
            },
            'logging': {
                'level': 'INFO',
                'file': './logs/jira_to_markdown.log',
                'console': True,
                'console_level': 'INFO'
            }
        }

    def _load_env_overrides(self):
        """Override config with environment variables."""
        # JIRA settings
        if os.getenv('JIRA_URL'):
            self._config.setdefault('jira', {})['url'] = os.getenv('JIRA_URL')
        if os.getenv('JIRA_USERNAME'):
            self._config.setdefault('jira', {})['username'] = os.getenv('JIRA_USERNAME')
        if os.getenv('JIRA_API_TOKEN'):
            self._config.setdefault('jira', {})['api_token'] = os.getenv('JIRA_API_TOKEN')

    def _validate(self):
        """Validate required configuration."""
        errors = []

        # Check JIRA URL
        jira_url = self.get('jira.url', '')
        if not jira_url:
            errors.append("JIRA URL is required (set JIRA_URL environment variable)")

        # Check username
        username = self.get('jira.username', '')
        if not username:
            errors.append("JIRA username is required (set JIRA_USERNAME environment variable)")

        # Check API token
        api_token = self.get('jira.api_token', '')
        if not api_token:
            errors.append("JIRA API token is required (set JIRA_API_TOKEN environment variable)")

        if errors:
            raise ConfigurationError("\n".join(errors))

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.

        Args:
            key: Configuration key (e.g., 'jira.url')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """
        Set configuration value using dot notation.

        Args:
            key: Configuration key (e.g., 'jira.url')
            value: Value to set
        """
        keys = key.split('.')
        config = self._config

        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    @property
    def jira_url(self) -> str:
        """Get JIRA URL."""
        return self.get('jira.url', '')

    @property
    def jira_username(self) -> str:
        """Get JIRA username."""
        return self.get('jira.username', '')

    @property
    def jira_api_token(self) -> str:
        """Get JIRA API token."""
        return self.get('jira.api_token', '')

    @property
    def jira_verify_ssl(self) -> bool:
        """Get SSL verification setting."""
        return self.get('jira.verify_ssl', True)

    @property
    def output_directory(self) -> str:
        """Get output directory."""
        return self.get('output.directory', './output')

    @property
    def output_filename_format(self) -> str:
        """Get output filename format."""
        return self.get('output.filename_format', '{key}.md')

    @property
    def output_overwrite(self) -> bool:
        """Get overwrite setting."""
        return self.get('output.overwrite', False)

    @property
    def log_level(self) -> str:
        """Get log level."""
        return self.get('logging.level', 'INFO')

    @property
    def log_file(self) -> str:
        """Get log file path."""
        return self.get('logging.file', './logs/jira_to_markdown.log')

    @property
    def log_console(self) -> bool:
        """Get console logging setting."""
        return self.get('logging.console', True)

    @property
    def log_console_level(self) -> str:
        """Get console log level."""
        return self.get('logging.console_level', 'INFO')

    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary."""
        return self._config.copy()
