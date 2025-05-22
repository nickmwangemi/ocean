import os
import yaml
from dataclasses import dataclass
from typing import Optional

@dataclass
class GitHubIntegrationConfig:
    api_token: str
    webhook_secret: str
    base_url: str
    integration_identifier: str

def load_github_integration_config() -> GitHubIntegrationConfig:
    # Load configuration from config.yaml file
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found at {config_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML configuration file: {e}")

    # Load configuration from environment variables if not specified in config.yaml
    api_token = config['integration']['config'].get('api_token', os.getenv('GITHUB_API_TOKEN'))
    webhook_secret = config['integration']['config'].get('webhook_secret', os.getenv('GITHUB_WEBHOOK_SECRET'))
    base_url = config['integration']['config'].get('base_url', os.getenv('GITHUB_BASE_URL', 'https://api.github.com'))
    integration_identifier = config['integration'].get('identifier', os.getenv('OCEAN__INTEGRATION__IDENTIFIER', 'github'))

    # Check for required environment variables
    required_env_vars = ["GITHUB_API_TOKEN", "GITHUB_WEBHOOK_SECRET"]
    missing_env_vars = [var for var in required_env_vars if not os.getenv(var) and not config['integration']['config'].get(var.lower())]

    if missing_env_vars:
        raise EnvironmentError(
            f"Missing environment variables: {', '.join(missing_env_vars)}"
        )

    return GitHubIntegrationConfig(
        api_token=api_token,
        webhook_secret=webhook_secret,
        base_url=base_url,
        integration_identifier=integration_identifier
    )
