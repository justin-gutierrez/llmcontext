"""
Ollama summarizer module for LLMContext.

This module provides integration with Ollama's local API for text summarization.
"""

import json
import requests
from typing import Optional, Dict, Any


def summarize_with_ollama(prompt: str, model: str = "mistral") -> str:
    """
    Send a summarization request to Ollama's local API.
    
    Args:
        prompt: The text prompt to send to the model
        model: The Ollama model to use (default: "mistral")
        
    Returns:
        The model's response text
        
    Raises:
        requests.RequestException: If the API request fails
        ValueError: If the response is invalid
    """
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        
        # Extract the response text
        if "response" in data:
            return data["response"]
        else:
            raise ValueError("Invalid response format from Ollama API")
            
    except requests.RequestException as e:
        raise requests.RequestException(f"Failed to connect to Ollama API: {e}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON response from Ollama API: {e}")
    except Exception as e:
        raise Exception(f"Unexpected error during Ollama API call: {e}")


def test_ollama_connection(model: str = "mistral") -> bool:
    """
    Test the connection to Ollama API.
    
    Args:
        model: The model to test with
        
    Returns:
        True if connection is successful, False otherwise
    """
    try:
        test_prompt = "Hello, this is a test message. Please respond with 'OK' if you can see this."
        response = summarize_with_ollama(test_prompt, model)
        return "OK" in response or len(response.strip()) > 0
    except Exception:
        return False


def get_available_models() -> list:
    """
    Get list of available Ollama models.
    
    Returns:
        List of available model names
        
    Raises:
        requests.RequestException: If the API request fails
    """
    url = "http://localhost:11434/api/tags"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if "models" in data:
            return [model["name"] for model in data["models"]]
        else:
            return []
            
    except requests.RequestException as e:
        raise requests.RequestException(f"Failed to get models from Ollama API: {e}")
    except json.JSONDecodeError:
        return [] 