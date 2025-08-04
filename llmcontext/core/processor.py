"""
Documentation Processor Module

This module processes all documentation chunks for a tool using the summarizer
and saves compressed output in organized markdown and JSON formats.
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, asdict
import logging
from datetime import datetime

from .summarizer import DocumentationSummarizer, SummaryResult
from .chunker import DocumentationChunker, DocumentChunk

logger = logging.getLogger(__name__)


@dataclass
class ProcessedDocumentation:
    """Represents processed documentation for a tool."""
    tool_name: str
    topic: str
    original_chunks: List[DocumentChunk]
    summarized_chunks: List[SummaryResult]
    metadata: Dict[str, Any]
    processing_stats: Dict[str, Any]


class DocumentationProcessor:
    """Processes documentation chunks into optimized, organized outputs."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        max_concurrent: int = 5,
        output_base_dir: Path = Path("docs"),
        preserve_original: bool = True
    ):
        """
        Initialize the documentation processor.
        
        Args:
            api_key: OpenAI API key
            model: OpenAI model for summarization
            max_concurrent: Maximum concurrent API calls
            output_base_dir: Base directory for output files
            preserve_original: Whether to preserve original chunks in output
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.max_concurrent = max_concurrent
        self.output_base_dir = output_base_dir
        self.preserve_original = preserve_original
        
        # Initialize components
        self.summarizer = DocumentationSummarizer(
            api_key=self.api_key,
            model=model,
            max_concurrent=max_concurrent
        )
        
        # Create output directory
        self.output_base_dir.mkdir(parents=True, exist_ok=True)
    
    def process_tool_documentation(
        self,
        tool_name: str,
        chunks_dir: Path,
        topics: Optional[List[str]] = None
    ) -> Dict[str, ProcessedDocumentation]:
        """
        Process all documentation chunks for a specific tool.
        
        Args:
            tool_name: Name of the tool/framework
            chunks_dir: Directory containing chunk files
            topics: Optional list of topics to process (if None, processes all)
            
        Returns:
            Dictionary mapping topics to ProcessedDocumentation objects
        """
        logger.info(f"Processing documentation for tool: {tool_name}")
        
        # Create tool output directory
        tool_output_dir = self.output_base_dir / tool_name
        tool_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Group chunks by topic
        topic_chunks = self._group_chunks_by_topic(chunks_dir, tool_name)
        
        # Filter topics if specified
        if topics:
            topic_chunks = {topic: chunks for topic, chunks in topic_chunks.items() 
                          if topic in topics}
        
        results = {}
        
        for topic, chunks in topic_chunks.items():
            logger.info(f"Processing topic: {topic} ({len(chunks)} chunks)")
            
            try:
                processed_doc = self._process_topic(
                    tool_name=tool_name,
                    topic=topic,
                    chunks=chunks,
                    output_dir=tool_output_dir
                )
                results[topic] = processed_doc
                
                logger.info(f"✅ Completed topic: {topic}")
                
            except Exception as e:
                logger.error(f"❌ Error processing topic {topic}: {e}")
                continue
        
        # Create tool-level summary
        self._create_tool_summary(tool_name, results, tool_output_dir)
        
        return results
    
    def _group_chunks_by_topic(self, chunks_dir: Path, tool_name: str) -> Dict[str, List[DocumentChunk]]:
        """
        Group chunk files by topic based on filename patterns.
        
        Args:
            chunks_dir: Directory containing chunk files
            tool_name: Name of the tool
            
        Returns:
            Dictionary mapping topics to lists of DocumentChunk objects
        """
        topic_chunks = {}
        
        # Find all chunk files for this tool
        chunk_files = list(chunks_dir.glob(f"{tool_name}_*.md"))
        
        for chunk_file in chunk_files:
            try:
                # Parse chunk file to extract topic and create DocumentChunk
                chunk = self._parse_chunk_file(chunk_file)
                if chunk:
                    # Extract topic from chunk metadata or filename
                    topic = self._extract_topic_from_chunk(chunk, chunk_file)
                    
                    if topic not in topic_chunks:
                        topic_chunks[topic] = []
                    
                    topic_chunks[topic].append(chunk)
                    
            except Exception as e:
                logger.warning(f"Error parsing chunk file {chunk_file}: {e}")
                continue
        
        # Sort chunks within each topic by chunk_id
        for topic in topic_chunks:
            topic_chunks[topic].sort(key=lambda x: x.chunk_id)
        
        return topic_chunks
    
    def _parse_chunk_file(self, chunk_file: Path) -> Optional[DocumentChunk]:
        """
        Parse a chunk file and create a DocumentChunk object.
        
        Args:
            chunk_file: Path to the chunk file
            
        Returns:
            DocumentChunk object or None if parsing fails
        """
        try:
            with open(chunk_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract chunk ID from filename
            chunk_id = chunk_file.stem
            
            # Parse metadata from content (if present)
            metadata = {}
            if "**Metadata:**" in content:
                try:
                    metadata_start = content.find("**Metadata:**") + len("**Metadata:**")
                    metadata_end = content.find("\n\n", metadata_start)
                    if metadata_end == -1:
                        metadata_end = content.find("---", metadata_start)
                    
                    if metadata_end != -1:
                        metadata_str = content[metadata_start:metadata_end].strip()
                        metadata = eval(metadata_str)  # Safe for our controlled format
                except:
                    pass
            
            # Extract actual content (after metadata section)
            content_start = content.find("---\n\n")
            if content_start != -1:
                actual_content = content[content_start + 4:]
            else:
                actual_content = content
            
            # Estimate token count
            estimated_tokens = len(actual_content.split()) * 1.3
            
            return DocumentChunk(
                content=actual_content,
                chunk_id=chunk_id,
                start_token=0,  # We don't have this info from file
                end_token=int(estimated_tokens),
                metadata=metadata,
                tags=metadata.get('tags', [])
            )
            
        except Exception as e:
            logger.error(f"Error parsing chunk file {chunk_file}: {e}")
            return None
    
    def _extract_topic_from_chunk(self, chunk: DocumentChunk, chunk_file: Path) -> str:
        """
        Extract topic from chunk metadata or filename.
        
        Args:
            chunk: DocumentChunk object
            chunk_file: Path to the chunk file
            
        Returns:
            Topic name
        """
        # Try to extract from metadata first
        metadata = chunk.metadata
        if 'document_id' in metadata:
            return metadata['document_id']
        
        # Extract from filename pattern
        filename = chunk_file.stem
        if '_' in filename:
            # Remove tool name and chunk number
            parts = filename.split('_')
            if len(parts) >= 2:
                return parts[1]  # Usually the topic/document_id
        
        # Fallback to filename
        return filename
    
    def _process_topic(
        self,
        tool_name: str,
        topic: str,
        chunks: List[DocumentChunk],
        output_dir: Path
    ) -> ProcessedDocumentation:
        """
        Process a specific topic's chunks.
        
        Args:
            tool_name: Name of the tool
            topic: Topic name
            chunks: List of DocumentChunk objects
            output_dir: Output directory for the tool
            
        Returns:
            ProcessedDocumentation object
        """
        start_time = time.time()
        
        # Convert chunks to format expected by summarizer
        chunk_dicts = [
            {
                'content': chunk.content,
                'chunk_id': chunk.chunk_id
            }
            for chunk in chunks
        ]
        
        # Summarize chunks
        logger.info(f"Summarizing {len(chunks)} chunks for topic: {topic}")
        summarized_chunks = self.summarizer.summarize_chunks(chunk_dicts, tool_name)
        
        # Create output files
        self._save_topic_outputs(tool_name, topic, chunks, summarized_chunks, output_dir)
        
        # Calculate processing statistics
        processing_time = time.time() - start_time
        stats = self._calculate_processing_stats(chunks, summarized_chunks, processing_time)
        
        # Create metadata
        metadata = {
            'tool_name': tool_name,
            'topic': topic,
            'processed_at': datetime.now().isoformat(),
            'model': self.model,
            'chunk_count': len(chunks),
            'summarized_count': len(summarized_chunks)
        }
        
        return ProcessedDocumentation(
            tool_name=tool_name,
            topic=topic,
            original_chunks=chunks,
            summarized_chunks=summarized_chunks,
            metadata=metadata,
            processing_stats=stats
        )
    
    def _save_topic_outputs(
        self,
        tool_name: str,
        topic: str,
        original_chunks: List[DocumentChunk],
        summarized_chunks: List[SummaryResult],
        output_dir: Path
    ):
        """
        Save topic outputs in both markdown and JSON formats.
        
        Args:
            tool_name: Name of the tool
            topic: Topic name
            original_chunks: Original DocumentChunk objects
            summarized_chunks: Summarized chunks
            output_dir: Output directory
        """
        # Create topic directory
        topic_dir = output_dir / topic
        topic_dir.mkdir(exist_ok=True)
        
        # Save markdown file
        markdown_file = topic_dir / f"{topic}.md"
        self._save_markdown_output(tool_name, topic, original_chunks, summarized_chunks, markdown_file)
        
        # Save JSON file
        json_file = topic_dir / f"{topic}.json"
        self._save_json_output(tool_name, topic, original_chunks, summarized_chunks, json_file)
        
        logger.info(f"Saved outputs to: {topic_dir}")
    
    def _save_markdown_output(
        self,
        tool_name: str,
        topic: str,
        original_chunks: List[DocumentChunk],
        summarized_chunks: List[SummaryResult],
        output_file: Path
    ):
        """Save topic output in markdown format."""
        with open(output_file, 'w', encoding='utf-8') as f:
            # Header
            f.write(f"# {tool_name.title()} - {topic.title()}\n\n")
            f.write(f"**Processed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Model:** {self.model}\n")
            f.write(f"**Chunks:** {len(original_chunks)}\n")
            f.write(f"**Summarized:** {len(summarized_chunks)}\n\n")
            
            # Processing statistics
            total_original_tokens = sum(len(chunk.content.split()) * 1.3 for chunk in original_chunks)
            total_summarized_tokens = sum(result.summarized_tokens for result in summarized_chunks)
            reduction = ((total_original_tokens - total_summarized_tokens) / total_original_tokens) * 100
            
            f.write(f"**Token Reduction:** {reduction:.1f}%\n")
            f.write(f"**Original Tokens:** {int(total_original_tokens)}\n")
            f.write(f"**Summarized Tokens:** {int(total_summarized_tokens)}\n\n")
            
            f.write("---\n\n")
            
            # Summarized content
            f.write("## Summarized Documentation\n\n")
            
            for i, result in enumerate(summarized_chunks, 1):
                f.write(f"### Chunk {i}: {result.chunk_id}\n\n")
                f.write(f"**Reduction:** {result.token_reduction:.1f}% | ")
                f.write(f"**Tokens:** {result.original_tokens} → {result.summarized_tokens} | ")
                f.write(f"**Time:** {result.processing_time:.2f}s\n\n")
                
                f.write(result.summarized_content)
                f.write("\n\n---\n\n")
            
            # Original content (if preserved)
            if self.preserve_original:
                f.write("## Original Documentation\n\n")
                
                for i, chunk in enumerate(original_chunks, 1):
                    f.write(f"### Original Chunk {i}: {chunk.chunk_id}\n\n")
                    f.write(f"**Tokens:** ~{int(len(chunk.content.split()) * 1.3)}\n\n")
                    
                    f.write(chunk.content)
                    f.write("\n\n---\n\n")
    
    def _save_json_output(
        self,
        tool_name: str,
        topic: str,
        original_chunks: List[DocumentChunk],
        summarized_chunks: List[SummaryResult],
        output_file: Path
    ):
        """Save topic output in JSON format."""
        output_data = {
            'tool_name': tool_name,
            'topic': topic,
            'processed_at': datetime.now().isoformat(),
            'model': self.model,
            'statistics': {
                'original_chunks': len(original_chunks),
                'summarized_chunks': len(summarized_chunks),
                'total_original_tokens': sum(len(chunk.content.split()) * 1.3 for chunk in original_chunks),
                'total_summarized_tokens': sum(result.summarized_tokens for result in summarized_chunks),
                'average_reduction': sum(result.token_reduction for result in summarized_chunks) / len(summarized_chunks) if summarized_chunks else 0
            },
            'summarized_chunks': [
                {
                    'chunk_id': result.chunk_id,
                    'content': result.summarized_content,
                    'original_tokens': result.original_tokens,
                    'summarized_tokens': result.summarized_tokens,
                    'reduction_percent': result.token_reduction,
                    'processing_time': result.processing_time,
                    'metadata': result.metadata
                }
                for result in summarized_chunks
            ]
        }
        
        # Add original chunks if preserved
        if self.preserve_original:
            output_data['original_chunks'] = [
                {
                    'chunk_id': chunk.chunk_id,
                    'content': chunk.content,
                    'estimated_tokens': int(len(chunk.content.split()) * 1.3),
                    'metadata': chunk.metadata,
                    'tags': chunk.tags
                }
                for chunk in original_chunks
            ]
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    def _calculate_processing_stats(
        self,
        original_chunks: List[DocumentChunk],
        summarized_chunks: List[SummaryResult],
        processing_time: float
    ) -> Dict[str, Any]:
        """Calculate processing statistics."""
        total_original_tokens = sum(len(chunk.content.split()) * 1.3 for chunk in original_chunks)
        total_summarized_tokens = sum(result.summarized_tokens for result in summarized_chunks)
        
        return {
            'total_original_tokens': int(total_original_tokens),
            'total_summarized_tokens': int(total_summarized_tokens),
            'overall_reduction_percent': ((total_original_tokens - total_summarized_tokens) / total_original_tokens) * 100 if total_original_tokens > 0 else 0,
            'average_reduction_percent': sum(result.token_reduction for result in summarized_chunks) / len(summarized_chunks) if summarized_chunks else 0,
            'total_processing_time': processing_time,
            'chunks_per_second': len(summarized_chunks) / processing_time if processing_time > 0 else 0
        }
    
    def _create_tool_summary(
        self,
        tool_name: str,
        results: Dict[str, ProcessedDocumentation],
        output_dir: Path
    ):
        """Create a summary file for the entire tool."""
        summary_file = output_dir / f"{tool_name}_summary.md"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"# {tool_name.title()} Documentation Summary\n\n")
            f.write(f"**Processed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Model:** {self.model}\n")
            f.write(f"**Topics:** {len(results)}\n\n")
            
            # Overall statistics
            total_original_chunks = sum(len(result.original_chunks) for result in results.values())
            total_summarized_chunks = sum(len(result.summarized_chunks) for result in results.values())
            total_processing_time = sum(result.processing_stats['total_processing_time'] for result in results.values())
            
            f.write(f"**Total Original Chunks:** {total_original_chunks}\n")
            f.write(f"**Total Summarized Chunks:** {total_summarized_chunks}\n")
            f.write(f"**Total Processing Time:** {total_processing_time:.2f}s\n\n")
            
            f.write("---\n\n")
            
            # Topic summaries
            f.write("## Topics\n\n")
            
            for topic, result in results.items():
                stats = result.processing_stats
                f.write(f"### {topic.title()}\n\n")
                f.write(f"- **Chunks:** {len(result.original_chunks)} → {len(result.summarized_chunks)}\n")
                f.write(f"- **Reduction:** {stats['overall_reduction_percent']:.1f}%\n")
                f.write(f"- **Tokens:** {stats['total_original_tokens']} → {stats['total_summarized_tokens']}\n")
                f.write(f"- **Processing Time:** {stats['total_processing_time']:.2f}s\n")
                f.write(f"- **Files:** `{topic}/{topic}.md`, `{topic}/{topic}.json`\n\n")
        
        logger.info(f"Created tool summary: {summary_file}")


# Convenience functions
def process_tool_documentation(
    tool_name: str,
    chunks_dir: Path,
    api_key: Optional[str] = None,
    model: str = "gpt-4o-mini",
    output_dir: Path = Path("docs"),
    topics: Optional[List[str]] = None
) -> Dict[str, ProcessedDocumentation]:
    """
    Convenience function to process documentation for a tool.
    
    Args:
        tool_name: Name of the tool
        chunks_dir: Directory containing chunk files
        api_key: OpenAI API key
        model: OpenAI model to use
        output_dir: Output directory
        topics: Optional list of topics to process
        
    Returns:
        Dictionary mapping topics to ProcessedDocumentation objects
    """
    processor = DocumentationProcessor(
        api_key=api_key,
        model=model,
        output_base_dir=output_dir
    )
    
    return processor.process_tool_documentation(tool_name, chunks_dir, topics)


def process_all_tools_documentation(
    chunks_base_dir: Path,
    api_key: Optional[str] = None,
    model: str = "gpt-4o-mini",
    output_dir: Path = Path("docs"),
    tools: Optional[List[str]] = None
) -> Dict[str, Dict[str, ProcessedDocumentation]]:
    """
    Process documentation for all tools in a chunks directory.
    
    Args:
        chunks_base_dir: Base directory containing tool chunk directories
        api_key: OpenAI API key
        model: OpenAI model to use
        output_dir: Output directory
        tools: Optional list of tools to process
        
    Returns:
        Dictionary mapping tools to their topic results
    """
    processor = DocumentationProcessor(
        api_key=api_key,
        model=model,
        output_base_dir=output_dir
    )
    
    all_results = {}
    
    # Find tool directories
    tool_dirs = [d for d in chunks_base_dir.iterdir() if d.is_dir()]
    
    if tools:
        tool_dirs = [d for d in tool_dirs if d.name in tools]
    
    for tool_dir in tool_dirs:
        tool_name = tool_dir.name
        logger.info(f"Processing tool: {tool_name}")
        
        try:
            results = processor.process_tool_documentation(tool_name, tool_dir)
            all_results[tool_name] = results
            
        except Exception as e:
            logger.error(f"Error processing tool {tool_name}: {e}")
            continue
    
    return all_results 