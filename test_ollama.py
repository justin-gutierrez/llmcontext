#!/usr/bin/env python3
"""
Test script for Ollama summarizer integration.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llmcontext.summarizer.ollama import summarize_with_ollama, test_ollama_connection, get_available_models


def test_basic_functionality():
    """Test basic Ollama functionality."""
    print("Testing Ollama integration...")
    
    # Test connection
    print("1. Testing connection...")
    if test_ollama_connection():
        print("   SUCCESS: Connection to Ollama API successful")
    else:
        print("   ERROR: Failed to connect to Ollama API")
        return False
    
    # Test available models
    print("2. Getting available models...")
    try:
        models = get_available_models()
        print(f"   Available models: {models}")
    except Exception as e:
        print(f"   ERROR: Failed to get models: {e}")
        return False
    
    # Test summarization
    print("3. Testing summarization...")
    test_prompt = """
    React is a JavaScript library for building user interfaces. It was developed by Facebook and is used to create interactive UIs. 
    React uses a component-based architecture where UIs are broken down into reusable components. 
    Each component manages its own state and can be composed to build complex interfaces.
    """
    
    try:
        response = summarize_with_ollama(test_prompt, "mistral")
        print(f"   SUCCESS: Got response ({len(response)} characters)")
        print(f"   Response preview: {response[:100]}...")
        return True
    except Exception as e:
        print(f"   ERROR: Failed to get summarization: {e}")
        return False


def test_custom_prompt():
    """Test with a custom summarization prompt."""
    print("\nTesting custom summarization prompt...")
    
    custom_prompt = """
    Please summarize the following documentation in a concise way, focusing on key concepts and usage examples:
    
    FastAPI is a modern, fast web framework for building APIs with Python 3.7+ based on standard Python type hints.
    The key features are: Fast: Very high performance, on par with NodeJS and Go (thanks to Starlette and Pydantic).
    Fast to code: Increase the speed to develop features by about 200% to 300%. Fewer bugs: Reduce about 40% of human-induced errors.
    Intuitive: Great editor support. Completion everywhere. Less time debugging. Easy: Designed to be easy to use and learn.
    Less time reading docs. Short: Minimize code duplication. Multiple features from each parameter declaration.
    Robust: Get production-ready code. With automatic interactive documentation. Based on open standards.
    """
    
    try:
        response = summarize_with_ollama(custom_prompt, "mistral")
        print(f"SUCCESS: Custom summarization completed ({len(response)} characters)")
        print(f"Summary: {response}")
        return True
    except Exception as e:
        print(f"ERROR: Custom summarization failed: {e}")
        return False


if __name__ == "__main__":
    print("=== Ollama Integration Test ===\n")
    
    # Test basic functionality
    if test_basic_functionality():
        print("\n✅ Basic functionality test PASSED")
        
        # Test custom prompt
        if test_custom_prompt():
            print("\n✅ Custom prompt test PASSED")
            print("\n🎉 All tests PASSED! Ollama integration is working correctly.")
        else:
            print("\n❌ Custom prompt test FAILED")
            sys.exit(1)
    else:
        print("\n❌ Basic functionality test FAILED")
        print("\nMake sure:")
        print("1. Ollama is running on localhost:11434")
        print("2. The 'mistral' model is available")
        print("3. You can test with: ollama run mistral")
        sys.exit(1) 