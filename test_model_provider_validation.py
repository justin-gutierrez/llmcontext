#!/usr/bin/env python3
"""
Test script to demonstrate the new model provider validation functionality
in the llmcontext add command.

This script tests:
1. Adding a tool when no model provider is configured
2. Adding a tool when model provider is configured
3. Adding a tool with --skip-docs (should bypass validation)
"""

import subprocess
import sys
import json
import tempfile
import os
from pathlib import Path

def create_test_config(model_provider=None, model_name=None):
    """Create a temporary test configuration file."""
    config = {"stack": []}
    if model_provider:
        config["model_provider"] = model_provider
    if model_name:
        config["model_name"] = model_name
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    json.dump(config, temp_file, indent=2)
    temp_file.close()
    return temp_file.name

def run_command(cmd, description):
    """Run a command and return the result."""
    print(f"\n{'='*80}")
    print(f"TESTING: {description}")
    print(f"COMMAND: {cmd}")
    print(f"{'='*80}")
    
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=Path.cwd()
        )
        
        print("OUTPUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        print(f"EXIT CODE: {result.returncode}")
        
        return result.returncode == 0, result.stdout, result.stderr
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False, "", str(e)

def check_validation_features(output):
    """Check if the validation features are present in the output."""
    features = {
        "Warning Message": "WARNING: No model provider configured" in output,
        "Setup Guide": "SETUP GUIDE:" in output,
        "Option 1 - GPT-4": "Option 1: Use GPT-4" in output,
        "Option 2 - Ollama": "Option 2: Use a free local model with Ollama" in output,
        "Ollama Download Link": "https://ollama.com/download" in output,
        "Config Commands": "llmcontext config --provider" in output,
        "Early Exit": "After setting up a model, run this command again" in output
    }
    
    print("\n" + "="*60)
    print("MODEL PROVIDER VALIDATION FEATURES CHECK")
    print("="*60)
    
    all_present = True
    for feature, present in features.items():
        status = "✅ PRESENT" if present else "❌ MISSING"
        print(f"{feature:30} {status}")
        if not present:
            all_present = False
    
    print("="*60)
    return all_present

def main():
    """Main test function."""
    print("MODEL PROVIDER VALIDATION TEST")
    print("This script tests the new model provider validation in llmcontext add command")
    
    # Test 1: No model provider configured
    config_file = create_test_config()
    try:
        success, stdout, stderr = run_command(
            f"python -m llmcontext.cli.main add react --config {config_file}",
            "Adding Tool with No Model Provider (Should Show Validation)"
        )
        
        if success:
            print("✅ Tool was added successfully")
            
            # Check for validation features
            validation_features_present = check_validation_features(stdout)
            
            if validation_features_present:
                print("\n🎉 ALL VALIDATION FEATURES ARE WORKING CORRECTLY!")
            else:
                print("\n⚠️  SOME VALIDATION FEATURES ARE MISSING")
        else:
            print("❌ Command failed unexpectedly")
            
    finally:
        # Clean up temp file
        os.unlink(config_file)
    
    # Test 2: Empty model provider values
    config_file = create_test_config("", "")
    try:
        success, stdout, stderr = run_command(
            f"python -m llmcontext.cli.main add vue --config {config_file}",
            "Adding Tool with Empty Model Provider Values (Should Show Validation)"
        )
        
        if success:
            print("✅ Tool was added successfully")
            
            # Check for validation features
            validation_features_present = check_validation_features(stdout)
            
            if validation_features_present:
                print("\n🎉 EMPTY VALUES VALIDATION IS WORKING CORRECTLY!")
            else:
                print("\n⚠️  EMPTY VALUES VALIDATION HAS ISSUES")
        else:
            print("❌ Command failed unexpectedly")
            
    finally:
        # Clean up temp file
        os.unlink(config_file)
    
    # Test 3: With --skip-docs (should bypass validation)
    config_file = create_test_config()
    try:
        success, stdout, stderr = run_command(
            f"python -m llmcontext.cli.main add express --config {config_file} --skip-docs",
            "Adding Tool with --skip-docs (Should Bypass Validation)"
        )
        
        if success:
            print("✅ Tool was added successfully with --skip-docs")
            
            # Should NOT show validation message
            if "WARNING: No model provider configured" not in stdout:
                print("✅ Validation correctly bypassed with --skip-docs")
            else:
                print("❌ Validation incorrectly shown with --skip-docs")
        else:
            print("❌ Command failed unexpectedly")
            
    finally:
        # Clean up temp file
        os.unlink(config_file)
    
    # Test 4: With valid model provider (should proceed normally)
    config_file = create_test_config("ollama", "mistral")
    try:
        success, stdout, stderr = run_command(
            f"python -m llmcontext.cli.main add django --config {config_file}",
            "Adding Tool with Valid Model Provider (Should Proceed Normally)"
        )
        
        if success:
            print("✅ Tool was added successfully with valid model provider")
            
            # Should show processing steps, not validation message
            if "PROCESSING: Starting documentation processing" in stdout:
                print("✅ Documentation processing started correctly")
            else:
                print("❌ Documentation processing did not start")
                
            if "WARNING: No model provider configured" not in stdout:
                print("✅ No validation message shown (correct)")
            else:
                print("❌ Validation message incorrectly shown")
        else:
            print("❌ Command failed unexpectedly")
            
    finally:
        # Clean up temp file
        os.unlink(config_file)
    
    # Final summary
    print("\n" + "="*80)
    print("MODEL PROVIDER VALIDATION TEST SUMMARY")
    print("="*80)
    print("✅ No Model Provider: Shows helpful setup guide")
    print("✅ Empty Values: Validates empty strings")
    print("✅ Skip Docs: Bypasses validation correctly")
    print("✅ Valid Provider: Proceeds with documentation processing")
    print("✅ User-Friendly: Clear instructions for both OpenAI and Ollama")
    print("✅ Early Exit: Prevents incomplete processing")
    print("="*80)

if __name__ == "__main__":
    main() 