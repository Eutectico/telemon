"""Configuration loader with environment variable support."""

import os
import yaml
from pathlib import Path
from dotenv import load_dotenv
from typing import Any, Dict


class ConfigLoader:
    """Loads and manages configuration from YAML and environment variables."""

    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize config loader.

        Args:
            config_path: Path to the YAML configuration file
        """
        # Load environment variables from .env file
        load_dotenv()

        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)

        # Replace environment variables in config
        config = self._resolve_env_vars(config)
        return config

    def _resolve_env_vars(self, config: Any) -> Any:
        """Recursively resolve environment variables in config.

        Environment variables are specified as ${VAR_NAME} in the YAML file.
        """
        if isinstance(config, dict):
            return {key: self._resolve_env_vars(value) for key, value in config.items()}
        elif isinstance(config, list):
            return [self._resolve_env_vars(item) for item in config]
        elif isinstance(config, str) and config.startswith("${") and config.endswith("}"):
            # Extract environment variable name
            env_var = config[2:-1]
            value = os.getenv(env_var)
            if value is None:
                raise ValueError(f"Environment variable {env_var} not set")
            return value
        return config

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation key.

        Args:
            key: Configuration key in dot notation (e.g., 'telegram.bot_token')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def get_telegram_token(self) -> str:
        """Get Telegram bot token."""
        token = self.get('telegram.bot_token')
        if not token:
            raise ValueError("Telegram bot token not configured")
        return token

    def get_authorized_users(self) -> list:
        """Get list of authorized Telegram user IDs."""
        return self.get('telegram.authorized_users', [])

    def get_prometheus_url(self) -> str:
        """Get Prometheus URL."""
        return self.get('prometheus.url', 'http://localhost:9090')

    def get_grafana_url(self) -> str:
        """Get Grafana URL."""
        return self.get('grafana.url', 'http://localhost:3000')

    def get_webhook_config(self) -> Dict[str, Any]:
        """Get Alertmanager webhook configuration."""
        return {
            'port': self.get('alertmanager.webhook_port', 9119),
            'path': self.get('alertmanager.webhook_path', '/alerts')
        }
