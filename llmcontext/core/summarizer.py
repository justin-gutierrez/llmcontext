"""
Documentation Summarizer Module

This module uses OpenAI's GPT-4 API to summarize documentation chunks into compressed,
LLM-optimized formats that retain essential information while removing fluff.
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
import logging
from openai import OpenAI
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

logger = logging.getLogger(__name__)


@dataclass
class SummaryResult:
    """Represents a summarized documentation chunk."""
    original_content: str
    summarized_content: str
    chunk_id: str
    token_reduction: float  # Percentage of tokens reduced
    original_tokens: int
    summarized_tokens: int
    metadata: Dict[str, any]
    processing_time: float


class DocumentationSummarizer:
    """Summarizes documentation chunks using OpenAI's GPT-4 API."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",  # Use gpt-4o-mini for cost efficiency
        max_retries: int = 3,
        retry_delay: float = 1.0,
        max_concurrent: int = 5,
        temperature: float = 0.1,  # Low temperature for consistent summarization
        max_tokens: int = 4000,  # Max tokens for summary output
        preserve_formatting: bool = True
    ):
        """
        Initialize the documentation summarizer.
        
        Args:
            api_key: OpenAI API key (will use environment variable if not provided)
            model: OpenAI model to use for summarization
            max_retries: Maximum number of retries for API calls
            retry_delay: Delay between retries in seconds
            max_concurrent: Maximum concurrent API calls
            temperature: Temperature for generation (0.0-1.0)
            max_tokens: Maximum tokens for summary output
            preserve_formatting: Whether to preserve markdown formatting
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        self.model = model
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.max_concurrent = max_concurrent
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.preserve_formatting = preserve_formatting
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        
        # Thread pool for concurrent processing
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent)
    
    def create_summarization_prompt(self, content: str, framework_name: str = "unknown") -> str:
        """
        Create an optimized prompt for documentation summarization.
        
        Args:
            content: Original documentation content
            framework_name: Name of the framework/tool being summarized
            
        Returns:
            Formatted prompt for GPT-4
        """
        prompt = f"""You are an expert technical documentation summarizer. Your task is to compress this {framework_name} documentation chunk into a concise, LLM-optimized format.

**CRITICAL REQUIREMENTS:**
1. **REMOVE FLUFF**: Eliminate marketing language, repetitive explanations, and verbose descriptions
2. **KEEP ESSENTIALS**: Preserve usage examples, code snippets, common errors, and practical information
3. **MAINTAIN STRUCTURE**: Keep headers, code blocks, and important formatting
4. **FOCUS ON PRACTICAL USE**: Prioritize information developers actually need
5. **COMPRESS AGGRESSIVELY**: Aim for 60-80% reduction while keeping all essential information

**WHAT TO KEEP:**
- Code examples and usage patterns
- Common errors and solutions
- API signatures and parameters
- Configuration options
- Step-by-step instructions
- Important warnings and notes

**WHAT TO REMOVE:**
- Marketing language and hype
- Repetitive explanations
- Verbose descriptions
- Unnecessary context
- Redundant information
- Promotional content

**FORMAT:**
- Use clear, concise language
- Preserve markdown formatting
- Keep code blocks intact
- Use bullet points for lists
- Maintain logical flow

Here's the documentation to summarize:

{content}

Provide a compressed, practical summary that retains all essential information while removing fluff:"""
        
        return prompt
    
    def summarize_chunk(self, content: str, chunk_id: str, framework_name: str = "unknown") -> SummaryResult:
        """
        Summarize a single documentation chunk.
        
        Args:
            content: Original documentation content
            chunk_id: Unique identifier for the chunk
            framework_name: Name of the framework/tool
            
        Returns:
            SummaryResult with original and summarized content
        """
        start_time = time.time()
        
        try:
            # Create prompt
            prompt = self.create_summarization_prompt(content, framework_name)
            
            # Estimate original tokens (rough approximation)
            original_tokens = len(content.split()) * 1.3  # Rough token estimation
            
            # Make API call with retries
            for attempt in range(self.max_retries):
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {
                                "role": "system",
                                "content": "You are an expert technical documentation summarizer. Provide concise, practical summaries that retain essential information while removing fluff."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        temperature=self.temperature,
                        max_tokens=self.max_tokens,
                        timeout=60
                    )
                    
                    summarized_content = response.choices[0].message.content.strip()
                    
                    # Estimate summarized tokens
                    summarized_tokens = len(summarized_content.split()) * 1.3
                    
                    # Calculate token reduction
                    token_reduction = ((original_tokens - summarized_tokens) / original_tokens) * 100 if original_tokens > 0 else 0
                    
                    processing_time = time.time() - start_time
                    
                    return SummaryResult(
                        original_content=content,
                        summarized_content=summarized_content,
                        chunk_id=chunk_id,
                        token_reduction=token_reduction,
                        original_tokens=int(original_tokens),
                        summarized_tokens=int(summarized_tokens),
                        metadata={
                            "model": self.model,
                            "framework": framework_name,
                            "attempts": attempt + 1,
                            "preserve_formatting": self.preserve_formatting
                        },
                        processing_time=processing_time
                    )
                    
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed for chunk {chunk_id}: {e}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
                    else:
                        raise
            
        except Exception as e:
            logger.error(f"Failed to summarize chunk {chunk_id}: {e}")
            processing_time = time.time() - start_time
            
            # Return original content as fallback
            return SummaryResult(
                original_content=content,
                summarized_content=content,  # Fallback to original
                chunk_id=chunk_id,
                token_reduction=0.0,
                original_tokens=len(content.split()) * 1.3,
                summarized_tokens=len(content.split()) * 1.3,
                metadata={
                    "model": self.model,
                    "framework": framework_name,
                    "error": str(e),
                    "fallback": True
                },
                processing_time=processing_time
            )
    
    def summarize_chunks(self, chunks: List[Dict], framework_name: str = "unknown") -> List[SummaryResult]:
        """
        Summarize multiple documentation chunks concurrently.
        
        Args:
            chunks: List of chunk dictionaries with 'content' and 'chunk_id' keys
            framework_name: Name of the framework/tool
            
        Returns:
            List of SummaryResult objects
        """
        results = []
        
        # Progress bar for chunk processing
        with tqdm(total=len(chunks), desc=f"Summarizing {framework_name}", unit="chunk") as pbar:
            # Process chunks with thread pool for concurrency
            with ThreadPoolExecutor(max_workers=self.max_concurrent) as executor:
                # Submit all tasks
                future_to_chunk = {
                    executor.submit(self.summarize_chunk, chunk['content'], chunk['chunk_id'], framework_name): chunk
                    for chunk in chunks
                }
                
                # Collect results as they complete
                for future in future_to_chunk:
                    try:
                        result = future.result()
                        results.append(result)
                        logger.info(f"Summarized chunk {result.chunk_id}: {result.token_reduction:.1f}% reduction")
                        pbar.set_postfix(
                            chunk_id=result.chunk_id[:20] + "..." if len(result.chunk_id) > 20 else result.chunk_id,
                            reduction=f"{result.token_reduction:.1f}%",
                            status="✅ Success"
                        )
                    except Exception as e:
                        chunk = future_to_chunk[future]
                        logger.error(f"Failed to summarize chunk {chunk['chunk_id']}: {e}")
                        # Add fallback result
                        results.append(SummaryResult(
                            original_content=chunk['content'],
                            summarized_content=chunk['content'],
                            chunk_id=chunk['chunk_id'],
                            token_reduction=0.0,
                            original_tokens=len(chunk['content'].split()) * 1.3,
                            summarized_tokens=len(chunk['content'].split()) * 1.3,
                            metadata={"error": str(e), "fallback": True},
                            processing_time=0.0
                        ))
                        pbar.set_postfix(
                            chunk_id=chunk['chunk_id'][:20] + "..." if len(chunk['chunk_id']) > 20 else chunk['chunk_id'],
                            status="❌ Error"
                        )
                    finally:
                        pbar.update(1)
        
        return results
    
    def summarize_file(self, file_path: Path, output_path: Optional[Path] = None) -> SummaryResult:
        """
        Summarize a single documentation file.
        
        Args:
            file_path: Path to the documentation file
            output_path: Path to save the summarized content (optional)
            
        Returns:
            SummaryResult object
        """
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract framework name from filename
        framework_name = file_path.stem
        
        # Summarize content
        result = self.summarize_chunk(content, framework_name, framework_name)
        
        # Save summarized content if output path provided
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"# {framework_name} - Summarized Documentation\n\n")
                f.write(f"**Original Tokens:** {result.original_tokens}\n")
                f.write(f"**Summarized Tokens:** {result.summarized_tokens}\n")
                f.write(f"**Reduction:** {result.token_reduction:.1f}%\n")
                f.write(f"**Processing Time:** {result.processing_time:.2f}s\n\n")
                f.write("---\n\n")
                f.write(result.summarized_content)
        
        return result
    
    def summarize_directory(self, input_dir: Path, output_dir: Path, framework_name: str = "unknown") -> List[SummaryResult]:
        """
        Summarize all documentation files in a directory.
        
        Args:
            input_dir: Directory containing documentation files
            output_dir: Directory to save summarized files
            framework_name: Name of the framework/tool
            
        Returns:
            List of SummaryResult objects
        """
        results = []
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get all markdown files
        files = list(input_dir.glob("*.md"))
        
        if not files:
            logger.warning(f"No markdown files found in {input_dir}")
            return results
        
        # Progress bar for file processing
        with tqdm(total=len(files), desc=f"Summarizing {framework_name} files", unit="file") as pbar:
            for file_path in files:
                try:
                    pbar.set_description(f"Summarizing {file_path.name}")
                    output_path = output_dir / f"summarized_{file_path.name}"
                    result = self.summarize_file(file_path, output_path)
                    results.append(result)
                    
                    logger.info(f"Summarized {file_path.name}: {result.token_reduction:.1f}% reduction")
                    pbar.set_postfix(
                        file=file_path.name[:20] + "..." if len(file_path.name) > 20 else file_path.name,
                        reduction=f"{result.token_reduction:.1f}%",
                        status="✅ Success"
                    )
                    
                except Exception as e:
                    logger.error(f"Error summarizing {file_path}: {e}")
                    pbar.set_postfix(
                        file=file_path.name[:20] + "..." if len(file_path.name) > 20 else file_path.name,
                        status="❌ Error"
                    )
                    continue
                finally:
                    pbar.update(1)
        
        return results
    
    def get_summary_statistics(self, results: List[SummaryResult]) -> Dict:
        """
        Get statistics about summarization results.
        
        Args:
            results: List of SummaryResult objects
            
        Returns:
            Dictionary with summary statistics
        """
        if not results:
            return {}
        
        total_original_tokens = sum(r.original_tokens for r in results)
        total_summarized_tokens = sum(r.summarized_tokens for r in results)
        total_processing_time = sum(r.processing_time for r in results)
        
        avg_reduction = sum(r.token_reduction for r in results) / len(results)
        successful_summaries = len([r for r in results if not r.metadata.get("fallback", False)])
        
        return {
            "total_files": len(results),
            "successful_summaries": successful_summaries,
            "failed_summaries": len(results) - successful_summaries,
            "total_original_tokens": total_original_tokens,
            "total_summarized_tokens": total_summarized_tokens,
            "overall_reduction_percent": ((total_original_tokens - total_summarized_tokens) / total_original_tokens) * 100 if total_original_tokens > 0 else 0,
            "average_reduction_percent": avg_reduction,
            "total_processing_time": total_processing_time,
            "average_processing_time": total_processing_time / len(results) if results else 0,
            "token_distribution": {
                "high_reduction": len([r for r in results if r.token_reduction > 70]),
                "medium_reduction": len([r for r in results if 40 <= r.token_reduction <= 70]),
                "low_reduction": len([r for r in results if r.token_reduction < 40])
            }
        }


# Convenience functions
def summarize_documentation_file(
    file_path: Path,
    api_key: Optional[str] = None,
    model: str = "gpt-4o-mini",
    output_path: Optional[Path] = None
) -> SummaryResult:
    """
    Convenience function to summarize a single documentation file.
    
    Args:
        file_path: Path to the documentation file
        api_key: OpenAI API key
        model: OpenAI model to use
        output_path: Path to save summarized content
        
    Returns:
        SummaryResult object
    """
    summarizer = DocumentationSummarizer(api_key=api_key, model=model)
    return summarizer.summarize_file(file_path, output_path)


def summarize_documentation_directory(
    input_dir: Path,
    output_dir: Path,
    api_key: Optional[str] = None,
    model: str = "gpt-4o-mini",
    framework_name: str = "unknown"
) -> List[SummaryResult]:
    """
    Convenience function to summarize all documentation files in a directory.
    
    Args:
        input_dir: Directory containing documentation files
        output_dir: Directory to save summarized files
        api_key: OpenAI API key
        model: OpenAI model to use
        framework_name: Name of the framework/tool
        
    Returns:
        List of SummaryResult objects
    """
    summarizer = DocumentationSummarizer(api_key=api_key, model=model)
    return summarizer.summarize_directory(input_dir, output_dir, framework_name)


def create_optimized_prompt_for_llm(summarized_content: str, framework_name: str) -> str:
    """
    Create an optimized prompt for LLM use with summarized documentation.
    
    Args:
        summarized_content: Summarized documentation content
        framework_name: Name of the framework/tool
        
    Returns:
        Optimized prompt for LLM consumption
    """
    prompt = f"""You are an expert {framework_name} developer. Use this compressed documentation to help with development tasks:

{summarized_content}

When answering questions about {framework_name}:
1. Reference specific examples and code snippets from the documentation
2. Provide practical, actionable solutions
3. Mention common errors and their solutions
4. Focus on real-world usage patterns
5. Keep responses concise and practical

What would you like to know about {framework_name}?"""
    
    return prompt 