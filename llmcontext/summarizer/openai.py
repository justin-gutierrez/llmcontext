"""
OpenAI summarizer module for LLMContext.

This module provides integration with OpenAI's API for text summarization.
"""

import os
from typing import Optional
from ..core.summarizer import DocumentationSummarizer


def summarize_with_openai(text: str, model: str = "gpt-4o-mini") -> str:
    """
    Send a summarization request to OpenAI's API.
    
    Args:
        text: The text to summarize
        model: The OpenAI model to use (default: "gpt-4o-mini")
        
    Returns:
        The model's summarized text
        
    Raises:
        ValueError: If OpenAI API key is not available
        Exception: If the API request fails
    """
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
    
    try:
        # Create summarizer instance
        summarizer = DocumentationSummarizer(
            api_key=api_key,
            model=model,
            temperature=0.1,  # Low temperature for consistent summarization
            max_tokens=4000
        )
        
        # Create a simple prompt for summarization
        prompt = f"""Please summarize the following text in a concise way, focusing on key information and removing unnecessary details:

{text}

Provide a clear, well-structured summary:"""
        
        # Use the summarizer's chunk summarization method
        result = summarizer.summarize_chunk(
            content=prompt,
            chunk_id="summary_request",
            framework_name="general"
        )
        
        return result.summarized_content
        
    except Exception as e:
        raise Exception(f"Failed to summarize with OpenAI: {e}")


def test_openai_connection(model: str = "gpt-4o-mini") -> bool:
    """
    Test the connection to OpenAI API.
    
    Args:
        model: The model to test with
        
    Returns:
        True if connection is successful, False otherwise
    """
    try:
        test_text = "This is a test message to verify OpenAI API connectivity."
        response = summarize_with_openai(test_text, model)
        return len(response.strip()) > 0
    except Exception:
        return False 