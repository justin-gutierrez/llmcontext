#!/usr/bin/env python3
"""
Test script for the updated llmcontext add command with documentation processing.
"""

import subprocess
import sys
import json
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return the result."""
    print(f"\n{'='*60}")
    print(f"TESTING: {description}")
    print(f"COMMAND: {cmd}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=Path.cwd()
        )
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        print(f"EXIT CODE: {result.returncode}")
        
        return result.returncode == 0, result.stdout, result.stderr
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False, "", str(e)

def check_file_exists(file_path, description):
    """Check if a file exists and print its status."""
    path = Path(file_path)
    exists = path.exists()
    print(f"CHECK: {description}")
    print(f"PATH: {file_path}")
    print(f"EXISTS: {exists}")
    if exists:
        print(f"SIZE: {path.stat().st_size} bytes")
    print()
    return exists

def main():
    """Main test function."""
    print("TESTING UPDATED LLMCONTEXT ADD COMMAND")
    print("This test will verify the documentation processing pipeline")
    
    # Test 1: Show current configuration
    success, stdout, stderr = run_command(
        "python -m llmcontext.cli.main config --show",
        "Show current model configuration"
    )
    
    if not success:
        print("WARNING: Could not show configuration, continuing anyway...")
    
    # Test 2: Add a tool with documentation processing
    success, stdout, stderr = run_command(
        "python -m llmcontext.cli.main add tailwind",
        "Add tailwind with documentation processing"
    )
    
    if success:
        print("SUCCESS: Tailwind added successfully")
    else:
        print("ERROR: Failed to add tailwind")
        return
    
    # Test 3: Check if raw documentation was downloaded
    raw_docs_exists = check_file_exists(
        "raw_docs/tailwind.md",
        "Raw documentation file"
    )
    
    # Test 4: Check if chunks were created
    chunks_dir_exists = check_file_exists(
        "chunks/tailwind",
        "Chunks directory"
    )
    
    if chunks_dir_exists:
        chunk_files = list(Path("chunks/tailwind").glob("*.md"))
        print(f"CHUNK FILES: Found {len(chunk_files)} chunk files")
        for chunk_file in chunk_files[:3]:  # Show first 3
            print(f"  - {chunk_file.name}")
        if len(chunk_files) > 3:
            print(f"  ... and {len(chunk_files) - 3} more")
    
    # Test 5: Check if processed documentation was created
    docs_dir_exists = check_file_exists(
        "docs/tailwind",
        "Processed documentation directory"
    )
    
    if docs_dir_exists:
        doc_files = list(Path("docs/tailwind").glob("*.md"))
        print(f"PROCESSED FILES: Found {len(doc_files)} processed files")
        for doc_file in doc_files[:3]:  # Show first 3
            print(f"  - {doc_file.name}")
        if len(doc_files) > 3:
            print(f"  ... and {len(doc_files) - 3} more")
    
    # Test 6: Check configuration was updated
    config_exists = check_file_exists(
        ".llmcontext.json",
        "Configuration file"
    )
    
    if config_exists:
        try:
            with open(".llmcontext.json", "r") as f:
                config = json.load(f)
            print("CONFIG CONTENT:")
            print(json.dumps(config, indent=2))
        except Exception as e:
            print(f"ERROR: Could not read config: {e}")
    
    # Test 7: Add another tool with skip-docs flag
    success, stdout, stderr = run_command(
        "python -m llmcontext.cli.main add react --skip-docs",
        "Add react with documentation processing skipped"
    )
    
    if success:
        print("SUCCESS: React added successfully (docs skipped)")
    else:
        print("ERROR: Failed to add react")
    
    # Test 8: Verify react was added but no docs processed
    if config_exists:
        try:
            with open(".llmcontext.json", "r") as f:
                config = json.load(f)
            if "react" in str(config.get("stack", [])):
                print("SUCCESS: React found in configuration")
            else:
                print("ERROR: React not found in configuration")
        except Exception as e:
            print(f"ERROR: Could not verify config: {e}")
    
    # Test 9: Check that no react docs were processed
    react_docs_exists = check_file_exists(
        "docs/react",
        "React documentation directory (should not exist)"
    )
    
    if not react_docs_exists:
        print("SUCCESS: No react documentation processed (as expected)")
    else:
        print("WARNING: React documentation was processed despite --skip-docs flag")
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Raw docs downloaded: {raw_docs_exists}")
    print(f"Chunks created: {chunks_dir_exists}")
    print(f"Processed docs created: {docs_dir_exists}")
    print(f"Configuration updated: {config_exists}")
    print("="*60)

if __name__ == "__main__":
    main() 