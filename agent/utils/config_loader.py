"""
Configuration loader
"""

import os
import yaml
from typing import Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def load_config(config_path: str = None) -> Dict:
    """
    Load configuration from YAML file
    
    Args:
        config_path: Path to configuration file (default: config.yaml or config.deployment.yaml)
        
    Returns:
        Configuration dictionary
    """
    # Check for deployment config first (for cloud platforms)
    if config_path is None:
        if os.path.exists("config.deployment.yaml"):
            config_path = "config.deployment.yaml"
            print("Using deployment configuration (optimized for cloud)")
        else:
            config_path = "config.yaml"
    
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        
        # Override with environment variables if present
        if "HUGGINGFACE_API_TOKEN" in os.environ:
            if "huggingface" not in config:
                config["huggingface"] = {}
            config["huggingface"]["api_token"] = os.environ["HUGGINGFACE_API_TOKEN"]
        
        return config
        
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    except Exception as e:
        raise Exception(f"Error loading configuration: {e}")

