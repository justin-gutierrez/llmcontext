"""
Configuration management for LLMContext.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


def get_config_path() -> Path:
    """
    Get the path to the .llmcontext.json configuration file.
    
    Returns:
        Path to the configuration file
    """
    return Path.cwd() / ".llmcontext.json"


def load_config() -> Dict[str, Any]:
    """
    Load the configuration from .llmcontext.json.
    
    Returns:
        Configuration dictionary
        
    Raises:
        FileNotFoundError: If the config file doesn't exist
        json.JSONDecodeError: If the config file is invalid JSON
    """
    config_path = get_config_path()
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_config(config: Dict[str, Any]) -> None:
    """
    Save configuration to .llmcontext.json.
    
    Args:
        config: Configuration dictionary to save
    """
    config_path = get_config_path()
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def get_config() -> Dict[str, Any]:
    """
    Get the current configuration with defaults for missing values.
    
    Returns:
        Configuration dictionary with defaults applied
    """
    try:
        config = load_config()
    except (FileNotFoundError, json.JSONDecodeError):
        # Return default configuration if file doesn't exist or is invalid
        config = {}
    
    # Apply defaults for missing values
    defaults = {
        "stack": [],
        "model_provider": "openai",  # Default to OpenAI
        "model_name": "gpt-4o-mini"  # Default OpenAI model
    }
    
    # Merge config with defaults
    for key, default_value in defaults.items():
        if key not in config:
            config[key] = default_value
    
    return config


def get_model_config() -> Dict[str, str]:
    """
    Get the model provider configuration.
    
    Returns:
        Dictionary with 'provider' and 'model' keys
    """
    config = get_config()
    return {
        "provider": config.get("model_provider", "openai"),
        "model": config.get("model_name", "gpt-4o-mini")
    }


def update_model_config(provider: str, model: str) -> None:
    """
    Update the model provider configuration.
    
    Args:
        provider: Model provider (e.g., 'openai', 'ollama')
        model: Model name (e.g., 'gpt-4o-mini', 'mistral')
    """
    config = get_config()
    config["model_provider"] = provider
    config["model_name"] = model
    save_config(config)


def get_stack() -> list:
    """
    Get the current tool stack.
    
    Returns:
        List of tools in the stack
    """
    config = get_config()
    return config.get("stack", [])


def update_stack(stack: list) -> None:
    """
    Update the tool stack.
    
    Args:
        stack: List of tools to set in the stack
    """
    config = get_config()
    config["stack"] = stack
    save_config(config)


def add_to_stack(tool: str) -> None:
    """
    Add a tool to the stack.
    
    Args:
        tool: Tool string to add (e.g., 'react@18')
    """
    config = get_config()
    stack = config.get("stack", [])
    
    if tool not in stack:
        stack.append(tool)
        config["stack"] = stack
        save_config(config)


def remove_from_stack(tool: str) -> None:
    """
    Remove a tool from the stack.
    
    Args:
        tool: Tool string to remove
    """
    config = get_config()
    stack = config.get("stack", [])
    
    if tool in stack:
        stack.remove(tool)
        config["stack"] = stack
        save_config(config)


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate the configuration structure.
    
    Args:
        config: Configuration dictionary to validate
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ["stack"]
    optional_fields = ["model_provider", "model_name"]
    
    # Check required fields
    for field in required_fields:
        if field not in config:
            return False
    
    # Validate stack is a list
    if not isinstance(config["stack"], list):
        return False
    
    # Validate optional fields if present
    if "model_provider" in config and not isinstance(config["model_provider"], str):
        return False
    
    if "model_name" in config and not isinstance(config["model_name"], str):
        return False
    
    return True


def create_default_config() -> Dict[str, Any]:
    """
    Create a default configuration.
    
    Returns:
        Default configuration dictionary
    """
    return {
        "stack": [],
        "model_provider": "openai",
        "model_name": "gpt-4o-mini"
    }


def init_config(force: bool = False) -> None:
    """
    Initialize the configuration file.
    
    Args:
        force: Whether to overwrite existing config file
    """
    config_path = get_config_path()
    
    if config_path.exists() and not force:
        raise FileExistsError(f"Configuration file already exists: {config_path}")
    
    default_config = create_default_config()
    save_config(default_config) 