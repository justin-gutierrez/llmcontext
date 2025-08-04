#!/usr/bin/env python3
"""
Test script for the summarize wrapper function.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llmcontext.summarizer import summarize, summarize_with_ollama, summarize_with_openai
from llmcontext.config import get_model_config, update_model_config


def test_config_loading():
    """Test that configuration is loaded correctly."""
    print("=== Configuration Loading Test ===\n")
    
    try:
        model_config = get_model_config()
        print(f"Current model config: {model_config}")
        print(f"Provider: {model_config['provider']}")
        print(f"Model: {model_config['model']}")
        return True
    except Exception as e:
        print(f"ERROR: Failed to load configuration: {e}")
        return False


def test_ollama_summarization():
    """Test Ollama summarization through the wrapper."""
    print("\n=== Ollama Summarization Test ===\n")
    
    # Save current config
    current_config = get_model_config()
    
    try:
        # Set to Ollama
        update_model_config("ollama", "mistral")
        print("Set provider to: ollama/mistral")
        
        # Test text
        test_text = """
        React is a JavaScript library for building user interfaces. It was developed by Facebook and is used to create interactive UIs. 
        React uses a component-based architecture where UIs are broken down into reusable components. 
        Each component manages its own state and can be composed to build complex interfaces.
        """
        
        print(f"Input text ({len(test_text)} characters):")
        print(test_text[:100] + "...")
        
        # Test summarization
        summary = summarize(test_text)
        print(f"\nSummary ({len(summary)} characters):")
        print(summary)
        
        return True
        
    except Exception as e:
        print(f"ERROR: Ollama summarization failed: {e}")
        return False
    finally:
        # Restore original config
        update_model_config(current_config["provider"], current_config["model"])


def test_openai_summarization():
    """Test OpenAI summarization through the wrapper."""
    print("\n=== OpenAI Summarization Test ===\n")
    
    # Check if OpenAI API key is available
    if not os.getenv("OPENAI_API_KEY"):
        print("SKIPPED: OPENAI_API_KEY not set")
        return True
    
    # Save current config
    current_config = get_model_config()
    
    try:
        # Set to OpenAI
        update_model_config("openai", "gpt-4o-mini")
        print("Set provider to: openai/gpt-4o-mini")
        
        # Test text
        test_text = """
        FastAPI is a modern, fast web framework for building APIs with Python 3.7+ based on standard Python type hints.
        The key features are: Fast: Very high performance, on par with NodeJS and Go (thanks to Starlette and Pydantic).
        Fast to code: Increase the speed to develop features by about 200% to 300%. Fewer bugs: Reduce about 40% of human-induced errors.
        Intuitive: Great editor support. Completion everywhere. Less time debugging. Easy: Designed to be easy to use and learn.
        """
        
        print(f"Input text ({len(test_text)} characters):")
        print(test_text[:100] + "...")
        
        # Test summarization
        summary = summarize(test_text)
        print(f"\nSummary ({len(summary)} characters):")
        print(summary)
        
        return True
        
    except Exception as e:
        print(f"ERROR: OpenAI summarization failed: {e}")
        return False
    finally:
        # Restore original config
        update_model_config(current_config["provider"], current_config["model"])


def test_invalid_provider():
    """Test handling of invalid provider."""
    print("\n=== Invalid Provider Test ===\n")
    
    # Save current config
    current_config = get_model_config()
    
    try:
        # Set to invalid provider
        update_model_config("invalid_provider", "invalid_model")
        print("Set provider to: invalid_provider/invalid_model")
        
        test_text = "This should fail."
        
        # This should raise an error
        try:
            summary = summarize(test_text)
            print("ERROR: Should have raised an exception")
            return False
        except ValueError as e:
            print(f"SUCCESS: Correctly raised ValueError: {e}")
            return True
        except Exception as e:
            print(f"ERROR: Unexpected exception: {e}")
            return False
            
    finally:
        # Restore original config
        update_model_config(current_config["provider"], current_config["model"])


def test_direct_functions():
    """Test direct summarizer functions."""
    print("\n=== Direct Functions Test ===\n")
    
    test_text = "This is a simple test message for direct function testing."
    success_count = 0
    total_tests = 0
    
    # Test Ollama directly
    total_tests += 1
    try:
        print("Testing summarize_with_ollama directly...")
        ollama_summary = summarize_with_ollama(test_text)
        print(f"Ollama summary: {ollama_summary[:50]}...")
        if len(ollama_summary.strip()) > 0:
            print("SUCCESS: Ollama direct test passed")
            success_count += 1
        else:
            print("ERROR: Ollama returned empty summary")
    except Exception as e:
        print(f"ERROR: Ollama direct test failed: {e}")
    
    # Test OpenAI directly (if API key available)
    if os.getenv("OPENAI_API_KEY"):
        total_tests += 1
        try:
            print("Testing summarize_with_openai directly...")
            openai_summary = summarize_with_openai(test_text)
            print(f"OpenAI summary: {openai_summary[:50]}...")
            if len(openai_summary.strip()) > 0:
                print("SUCCESS: OpenAI direct test passed")
                success_count += 1
            else:
                print("ERROR: OpenAI returned empty summary")
        except Exception as e:
            print(f"ERROR: OpenAI direct test failed: {e}")
    else:
        print("Skipping OpenAI direct test (no API key)")
    
    # Return True if at least one test passed (Ollama worked)
    return success_count > 0


if __name__ == "__main__":
    print("=== Summarize Wrapper Test Suite ===\n")
    
    tests = [
        ("Configuration Loading", test_config_loading),
        ("Ollama Summarization", test_ollama_summarization),
        ("OpenAI Summarization", test_openai_summarization),
        ("Invalid Provider", test_invalid_provider),
        ("Direct Functions", test_direct_functions)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED\n")
        else:
            print(f"❌ {test_name} FAILED\n")
    
    print(f"=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests PASSED! Summarize wrapper is working correctly.")
    else:
        print("❌ Some tests FAILED. Please check the implementation.")
        sys.exit(1) 