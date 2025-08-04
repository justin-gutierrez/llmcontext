"""
Embeddings Module

This module generates embeddings from compressed documentation chunks using OpenAI's
text-embedding-3-large model and stores them with metadata for vector search.
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, asdict
import logging
from datetime import datetime
import numpy as np
from openai import OpenAI

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingResult:
    """Represents an embedding result for a chunk."""
    chunk_id: str
    content: str
    embedding: List[float]
    metadata: Dict[str, Any]
    processing_time: float
    token_count: int


@dataclass
class EmbeddingBatch:
    """Represents a batch of embedding results."""
    tool_name: str
    topic: str
    embeddings: List[EmbeddingResult]
    batch_metadata: Dict[str, Any]
    total_tokens: int
    total_processing_time: float


class EmbeddingGenerator:
    """Generates embeddings from compressed documentation chunks."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "text-embedding-3-large",
        batch_size: int = 100,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        output_dir: Path = Path("embeddings")
    ):
        """
        Initialize the embedding generator.
        
        Args:
            api_key: OpenAI API key
            model: OpenAI embedding model to use
            batch_size: Number of texts to embed in a single API call
            max_retries: Maximum number of retries for failed API calls
            retry_delay: Delay between retries in seconds
            output_dir: Directory to store embedding files
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        self.model = model
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.output_dir = output_dir
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Model dimensions for text-embedding-3-large
        self.embedding_dimensions = 3072
        
        logger.info(f"Initialized EmbeddingGenerator with model: {model}")
    
    def generate_embeddings_from_processed_docs(
        self,
        docs_dir: Path,
        tools: Optional[List[str]] = None,
        topics: Optional[List[str]] = None
    ) -> Dict[str, Dict[str, EmbeddingBatch]]:
        """
        Generate embeddings from processed documentation files.
        
        Args:
            docs_dir: Directory containing processed documentation
            tools: Optional list of tools to process (if None, processes all)
            topics: Optional list of topics to process (if None, processes all)
            
        Returns:
            Dictionary mapping tools to their topic embedding batches
        """
        logger.info(f"Generating embeddings from processed docs in: {docs_dir}")
        
        all_results = {}
        
        # Find tool directories
        tool_dirs = [d for d in docs_dir.iterdir() if d.is_dir() and not d.name.endswith('_summary')]
        
        if tools:
            tool_dirs = [d for d in tool_dirs if d.name in tools]
        
        for tool_dir in tool_dirs:
            tool_name = tool_dir.name
            logger.info(f"Processing tool: {tool_name}")
            
            try:
                tool_results = self._process_tool_embeddings(tool_dir, topics)
                all_results[tool_name] = tool_results
                
            except Exception as e:
                logger.error(f"Error processing tool {tool_name}: {e}")
                continue
        
        return all_results
    
    def _process_tool_embeddings(
        self,
        tool_dir: Path,
        topics: Optional[List[str]] = None
    ) -> Dict[str, EmbeddingBatch]:
        """
        Process embeddings for a specific tool.
        
        Args:
            tool_dir: Tool directory containing topic subdirectories
            topics: Optional list of topics to process
            
        Returns:
            Dictionary mapping topics to EmbeddingBatch objects
        """
        tool_name = tool_dir.name
        topic_results = {}
        
        # Find topic directories
        topic_dirs = [d for d in tool_dir.iterdir() if d.is_dir()]
        
        if topics:
            topic_dirs = [d for d in topic_dirs if d.name in topics]
        
        for topic_dir in topic_dirs:
            topic_name = topic_dir.name
            logger.info(f"Processing topic: {topic_name}")
            
            try:
                # Look for JSON file first (preferred)
                json_file = topic_dir / f"{topic_name}.json"
                if json_file.exists():
                    batch = self._process_json_file(json_file, tool_name, topic_name)
                else:
                    # Fallback to markdown file
                    md_file = topic_dir / f"{topic_name}.md"
                    if md_file.exists():
                        batch = self._process_markdown_file(md_file, tool_name, topic_name)
                    else:
                        logger.warning(f"No documentation files found in {topic_dir}")
                        continue
                
                topic_results[topic_name] = batch
                
                # Save embeddings
                self._save_embeddings(batch)
                
                logger.info(f"✅ Completed topic: {topic_name}")
                
            except Exception as e:
                logger.error(f"Error processing topic {topic_name}: {e}")
                continue
        
        return topic_results
    
    def _process_json_file(
        self,
        json_file: Path,
        tool_name: str,
        topic_name: str
    ) -> EmbeddingBatch:
        """
        Process embeddings from a JSON documentation file.
        
        Args:
            json_file: Path to JSON documentation file
            tool_name: Name of the tool
            topic_name: Name of the topic
            
        Returns:
            EmbeddingBatch object
        """
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract summarized chunks
        summarized_chunks = data.get('summarized_chunks', [])
        
        if not summarized_chunks:
            raise ValueError(f"No summarized chunks found in {json_file}")
        
        # Generate embeddings for each chunk
        embeddings = []
        total_tokens = 0
        total_processing_time = 0
        
        for chunk_data in summarized_chunks:
            try:
                embedding_result = self._generate_single_embedding(
                    chunk_data['content'],
                    chunk_data['chunk_id'],
                    tool_name,
                    topic_name,
                    json_file,
                    chunk_data
                )
                
                embeddings.append(embedding_result)
                total_tokens += embedding_result.token_count
                total_processing_time += embedding_result.processing_time
                
            except Exception as e:
                logger.error(f"Error generating embedding for chunk {chunk_data.get('chunk_id', 'unknown')}: {e}")
                continue
        
        # Create batch metadata
        batch_metadata = {
            'tool_name': tool_name,
            'topic': topic_name,
            'source_file': str(json_file),
            'processed_at': datetime.now().isoformat(),
            'model': self.model,
            'embedding_dimensions': self.embedding_dimensions,
            'total_chunks': len(summarized_chunks),
            'successful_embeddings': len(embeddings),
            'original_metadata': {
                'processed_at': data.get('processed_at'),
                'model': data.get('model'),
                'statistics': data.get('statistics', {})
            }
        }
        
        return EmbeddingBatch(
            tool_name=tool_name,
            topic=topic_name,
            embeddings=embeddings,
            batch_metadata=batch_metadata,
            total_tokens=total_tokens,
            total_processing_time=total_processing_time
        )
    
    def _process_markdown_file(
        self,
        md_file: Path,
        tool_name: str,
        topic_name: str
    ) -> EmbeddingBatch:
        """
        Process embeddings from a markdown documentation file.
        
        Args:
            md_file: Path to markdown documentation file
            tool_name: Name of the tool
            topic_name: Name of the topic
            
        Returns:
            EmbeddingBatch object
        """
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract summarized chunks from markdown
        chunks = self._extract_chunks_from_markdown(content)
        
        if not chunks:
            raise ValueError(f"No chunks found in {md_file}")
        
        # Generate embeddings for each chunk
        embeddings = []
        total_tokens = 0
        total_processing_time = 0
        
        for i, chunk_content in enumerate(chunks):
            try:
                chunk_id = f"{topic_name}_chunk_{i:03d}"
                
                embedding_result = self._generate_single_embedding(
                    chunk_content,
                    chunk_id,
                    tool_name,
                    topic_name,
                    md_file,
                    {'chunk_index': i}
                )
                
                embeddings.append(embedding_result)
                total_tokens += embedding_result.token_count
                total_processing_time += embedding_result.processing_time
                
            except Exception as e:
                logger.error(f"Error generating embedding for chunk {i}: {e}")
                continue
        
        # Create batch metadata
        batch_metadata = {
            'tool_name': tool_name,
            'topic': topic_name,
            'source_file': str(md_file),
            'processed_at': datetime.now().isoformat(),
            'model': self.model,
            'embedding_dimensions': self.embedding_dimensions,
            'total_chunks': len(chunks),
            'successful_embeddings': len(embeddings),
            'extraction_method': 'markdown_parsing'
        }
        
        return EmbeddingBatch(
            tool_name=tool_name,
            topic=topic_name,
            embeddings=embeddings,
            batch_metadata=batch_metadata,
            total_tokens=total_tokens,
            total_processing_time=total_processing_time
        )
    
    def _extract_chunks_from_markdown(self, content: str) -> List[str]:
        """
        Extract chunk content from markdown file.
        
        Args:
            content: Markdown content
            
        Returns:
            List of chunk contents
        """
        chunks = []
        
        # Split by chunk headers
        lines = content.split('\n')
        current_chunk = []
        in_chunk = False
        
        for line in lines:
            if line.startswith('### Chunk'):
                if current_chunk and in_chunk:
                    chunks.append('\n'.join(current_chunk).strip())
                current_chunk = []
                in_chunk = True
                continue
            
            if in_chunk and line.strip():
                current_chunk.append(line)
        
        # Add the last chunk
        if current_chunk and in_chunk:
            chunks.append('\n'.join(current_chunk).strip())
        
        return chunks
    
    def _generate_single_embedding(
        self,
        content: str,
        chunk_id: str,
        tool_name: str,
        topic_name: str,
        source_file: Path,
        chunk_metadata: Dict[str, Any]
    ) -> EmbeddingResult:
        """
        Generate embedding for a single chunk.
        
        Args:
            content: Text content to embed
            chunk_id: Unique identifier for the chunk
            tool_name: Name of the tool
            topic_name: Name of the topic
            source_file: Source file path
            chunk_metadata: Additional chunk metadata
            
        Returns:
            EmbeddingResult object
        """
        start_time = time.time()
        
        # Estimate token count (rough approximation)
        token_count = len(content.split()) * 1.3
        
        # Generate embedding with retry logic
        embedding = None
        for attempt in range(self.max_retries):
            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=content,
                    encoding_format="float"
                )
                
                embedding = response.data[0].embedding
                break
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    logger.warning(f"Embedding generation failed (attempt {attempt + 1}): {e}")
                    time.sleep(self.retry_delay)
                else:
                    raise e
        
        if embedding is None:
            raise ValueError("Failed to generate embedding after all retries")
        
        processing_time = time.time() - start_time
        
        # Create metadata
        metadata = {
            'tool_name': tool_name,
            'topic': topic_name,
            'source_file': str(source_file),
            'chunk_id': chunk_id,
            'token_count': int(token_count),
            'embedding_dimensions': len(embedding),
            'processing_time': processing_time,
            'model': self.model,
            **chunk_metadata
        }
        
        return EmbeddingResult(
            chunk_id=chunk_id,
            content=content,
            embedding=embedding,
            metadata=metadata,
            processing_time=processing_time,
            token_count=int(token_count)
        )
    
    def _save_embeddings(self, batch: EmbeddingBatch):
        """
        Save embeddings to files.
        
        Args:
            batch: EmbeddingBatch object to save
        """
        # Create tool directory
        tool_dir = self.output_dir / batch.tool_name
        tool_dir.mkdir(parents=True, exist_ok=True)
        
        # Save JSON file with all embeddings
        json_file = tool_dir / f"{batch.topic}_embeddings.json"
        
        json_data = {
            'batch_metadata': batch.batch_metadata,
            'embeddings': [
                {
                    'chunk_id': result.chunk_id,
                    'content': result.content,
                    'embedding': result.embedding,
                    'metadata': result.metadata
                }
                for result in batch.embeddings
            ],
            'statistics': {
                'total_embeddings': len(batch.embeddings),
                'total_tokens': batch.total_tokens,
                'total_processing_time': batch.total_processing_time,
                'average_processing_time': batch.total_processing_time / len(batch.embeddings) if batch.embeddings else 0,
                'embedding_dimensions': self.embedding_dimensions
            }
        }
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        # Save numpy array for efficient loading
        np_file = tool_dir / f"{batch.topic}_embeddings.npy"
        
        # Create structured array with embeddings and metadata
        dtype = [
            ('chunk_id', 'U100'),
            ('embedding', f'f{self.embedding_dimensions}'),
            ('tool_name', 'U50'),
            ('topic', 'U50'),
            ('token_count', 'i4'),
            ('processing_time', 'f4')
        ]
        
        embeddings_array = np.array([
            (
                result.chunk_id,
                result.embedding,
                batch.tool_name,
                batch.topic,
                result.token_count,
                result.processing_time
            )
            for result in batch.embeddings
        ], dtype=dtype)
        
        np.save(np_file, embeddings_array)
        
        # Save metadata separately
        metadata_file = tool_dir / f"{batch.topic}_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(batch.batch_metadata, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved embeddings to: {json_file}, {np_file}, {metadata_file}")
    
    def get_embedding_statistics(self, results: Dict[str, Dict[str, EmbeddingBatch]]) -> Dict[str, Any]:
        """
        Calculate statistics for embedding generation results.
        
        Args:
            results: Results from generate_embeddings_from_processed_docs
            
        Returns:
            Dictionary with statistics
        """
        total_tools = len(results)
        total_topics = sum(len(tool_results) for tool_results in results.values())
        total_embeddings = 0
        total_tokens = 0
        total_processing_time = 0
        
        for tool_results in results.values():
            for batch in tool_results.values():
                total_embeddings += len(batch.embeddings)
                total_tokens += batch.total_tokens
                total_processing_time += batch.total_processing_time
        
        return {
            'total_tools': total_tools,
            'total_topics': total_topics,
            'total_embeddings': total_embeddings,
            'total_tokens': total_tokens,
            'total_processing_time': total_processing_time,
            'average_processing_time_per_embedding': total_processing_time / total_embeddings if total_embeddings > 0 else 0,
            'embeddings_per_second': total_embeddings / total_processing_time if total_processing_time > 0 else 0,
            'model': self.model,
            'embedding_dimensions': self.embedding_dimensions
        }


# Convenience functions
def generate_embeddings_from_docs(
    docs_dir: Path,
    api_key: Optional[str] = None,
    model: str = "text-embedding-3-large",
    tools: Optional[List[str]] = None,
    topics: Optional[List[str]] = None,
    output_dir: Path = Path("embeddings")
) -> Dict[str, Dict[str, EmbeddingBatch]]:
    """
    Convenience function to generate embeddings from processed documentation.
    
    Args:
        docs_dir: Directory containing processed documentation
        api_key: OpenAI API key
        model: OpenAI embedding model to use
        tools: Optional list of tools to process
        topics: Optional list of topics to process
        output_dir: Output directory for embeddings
        
    Returns:
        Dictionary mapping tools to their topic embedding batches
    """
    generator = EmbeddingGenerator(
        api_key=api_key,
        model=model,
        output_dir=output_dir
    )
    
    return generator.generate_embeddings_from_processed_docs(docs_dir, tools, topics)


def load_embeddings(embeddings_dir: Path, tool_name: str, topic: str) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Load embeddings from saved files.
    
    Args:
        embeddings_dir: Directory containing embeddings
        tool_name: Name of the tool
        topic: Name of the topic
        
    Returns:
        Tuple of (embeddings_array, metadata)
    """
    tool_dir = embeddings_dir / tool_name
    
    # Load numpy array
    np_file = tool_dir / f"{topic}_embeddings.npy"
    embeddings_array = np.load(np_file)
    
    # Load metadata
    metadata_file = tool_dir / f"{topic}_metadata.json"
    with open(metadata_file, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    return embeddings_array, metadata 