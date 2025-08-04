"""
LLMContext - Universal sidecar service + CLI for framework detection and documentation optimization.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .cli.main import app
from .config import get_config, get_model_config, update_model_config

__all__ = ["app", "get_config", "get_model_config", "update_model_config"] 