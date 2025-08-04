"""
Summarizer package for LLMContext.

This package contains different summarization backends including OpenAI and Ollama.
"""

from .ollama import summarize_with_ollama
from .openai import summarize_with_openai
from ..config import get_model_config


def summarize(text: str) -> str:
    """
    Summarize text using the configured model provider.
    
    This function automatically selects the appropriate summarization method
    based on the configuration in .llmcontext.json.
    
    Args:
        text: The text to summarize
        
    Returns:
        The summarized text
        
    Raises:
        ValueError: If the model provider is not supported
        Exception: If summarization fails
    """
    # Load configuration
    model_config = get_model_config()
    provider = model_config["provider"]
    model = model_config["model"]
    
    # Route to appropriate summarizer
    if provider == "ollama":
        return summarize_with_ollama(text, model)
    elif provider == "openai":
        return summarize_with_openai(text, model)
    else:
        raise ValueError(f"Unsupported model provider: {provider}. Supported providers: 'ollama', 'openai'")


__all__ = ["summarize", "summarize_with_ollama", "summarize_with_openai"] 