"""
Documentation Chunker Module

This module handles splitting raw documentation files into optimal chunks for LLM processing.
It uses intelligent splitting strategies to maintain context and readability.
"""

import re
import math
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import tiktoken
from enum import Enum


class ChunkStrategy(Enum):
    """Different strategies for chunking documentation."""
    SEMANTIC = "semantic"  # Split by semantic boundaries (headers, sections)
    TOKEN_COUNT = "token_count"  # Split by token count only
    HYBRID = "hybrid"  # Combine semantic boundaries with token limits


@dataclass
class DocumentChunk:
    """Represents a chunk of documentation."""
    content: str
    chunk_id: str
    start_token: int
    end_token: int
    metadata: Dict[str, any]
    overlap_tokens: int = 0


class DocumentationChunker:
    """Splits documentation into optimal chunks for LLM processing."""
    
    def __init__(
        self,
        target_chunk_size: int = 1000,
        min_chunk_size: int = 800,
        max_chunk_size: int = 1200,
        overlap_tokens: int = 100,
        strategy: ChunkStrategy = ChunkStrategy.HYBRID,
        encoding_model: str = "cl100k_base"  # GPT-4 tokenizer
    ):
        """
        Initialize the documentation chunker.
        
        Args:
            target_chunk_size: Target number of tokens per chunk
            min_chunk_size: Minimum tokens per chunk
            max_chunk_size: Maximum tokens per chunk
            overlap_tokens: Number of overlapping tokens between chunks
            strategy: Chunking strategy to use
            encoding_model: Tokenizer model to use
        """
        self.target_chunk_size = target_chunk_size
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.overlap_tokens = overlap_tokens
        self.strategy = strategy
        
        # Initialize tokenizer
        try:
            self.tokenizer = tiktoken.get_encoding(encoding_model)
        except Exception as e:
            # Fallback to a simple character-based approximation
            print(f"Warning: Could not load tokenizer {encoding_model}: {e}")
            print("Falling back to character-based token estimation")
            self.tokenizer = None
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text using the tokenizer.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens
        """
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        else:
            # Fallback: rough approximation (1 token ≈ 4 characters)
            return len(text) // 4
    
    def split_document(self, content: str, document_id: str = "unknown") -> List[DocumentChunk]:
        """
        Split a document into chunks.
        
        Args:
            content: Raw document content
            document_id: Unique identifier for the document
            
        Returns:
            List of document chunks
        """
        if self.strategy == ChunkStrategy.SEMANTIC:
            return self._split_semantic(content, document_id)
        elif self.strategy == ChunkStrategy.TOKEN_COUNT:
            return self._split_by_tokens(content, document_id)
        elif self.strategy == ChunkStrategy.HYBRID:
            return self._split_hybrid(content, document_id)
        else:
            raise ValueError(f"Unknown chunking strategy: {self.strategy}")
    
    def _split_semantic(self, content: str, document_id: str) -> List[DocumentChunk]:
        """
        Split document by semantic boundaries (headers, sections).
        
        Args:
            content: Raw document content
            document_id: Document identifier
            
        Returns:
            List of semantic chunks
        """
        chunks = []
        
        # Split by markdown headers
        header_pattern = r'^(#{1,6})\s+(.+)$'
        lines = content.split('\n')
        
        current_chunk = []
        current_tokens = 0
        chunk_start = 0
        chunk_id = 0
        
        for i, line in enumerate(lines):
            line_tokens = self.count_tokens(line + '\n')
            
            # Check if this line is a header
            header_match = re.match(header_pattern, line)
            
            # Start new chunk if:
            # 1. We hit a header and current chunk is substantial
            # 2. Current chunk exceeds max size
            # 3. We're at the end of the document
            should_split = (
                (header_match and current_tokens >= self.min_chunk_size) or
                current_tokens >= self.max_chunk_size or
                i == len(lines) - 1
            )
            
            if should_split and current_chunk:
                # Create chunk
                chunk_content = '\n'.join(current_chunk)
                chunk = DocumentChunk(
                    content=chunk_content,
                    chunk_id=f"{document_id}_chunk_{chunk_id:03d}",
                    start_token=chunk_start,
                    end_token=chunk_start + current_tokens,
                    metadata={
                        "strategy": "semantic",
                        "header_level": self._get_header_level(current_chunk[0]) if current_chunk else None,
                        "line_count": len(current_chunk),
                        "document_id": document_id
                    }
                )
                chunks.append(chunk)
                
                # Start new chunk
                chunk_id += 1
                chunk_start += current_tokens
                current_chunk = [line]
                current_tokens = line_tokens
            else:
                current_chunk.append(line)
                current_tokens += line_tokens
        
        return chunks
    
    def _split_by_tokens(self, content: str, document_id: str) -> List[DocumentChunk]:
        """
        Split document by token count only.
        
        Args:
            content: Raw document content
            document_id: Document identifier
            
        Returns:
            List of token-based chunks
        """
        chunks = []
        total_tokens = self.count_tokens(content)
        
        # Calculate number of chunks needed
        num_chunks = math.ceil(total_tokens / self.target_chunk_size)
        
        for i in range(num_chunks):
            start_token = i * self.target_chunk_size
            end_token = min((i + 1) * self.target_chunk_size, total_tokens)
            
            # Extract chunk content
            chunk_content = self._extract_text_by_tokens(content, start_token, end_token)
            
            chunk = DocumentChunk(
                content=chunk_content,
                chunk_id=f"{document_id}_chunk_{i:03d}",
                start_token=start_token,
                end_token=end_token,
                metadata={
                    "strategy": "token_count",
                    "chunk_index": i,
                    "total_chunks": num_chunks,
                    "document_id": document_id
                }
            )
            chunks.append(chunk)
        
        return chunks
    
    def _split_hybrid(self, content: str, document_id: str) -> List[DocumentChunk]:
        """
        Split document using hybrid approach: semantic boundaries with token limits.
        
        Args:
            content: Raw document content
            document_id: Document identifier
            
        Returns:
            List of hybrid chunks
        """
        chunks = []
        
        # First, split by semantic boundaries
        semantic_chunks = self._split_semantic(content, document_id)
        
        # Then, further split large semantic chunks by token count
        for i, semantic_chunk in enumerate(semantic_chunks):
            if self.count_tokens(semantic_chunk.content) <= self.max_chunk_size:
                # Chunk is already within size limits
                semantic_chunk.chunk_id = f"{document_id}_hybrid_{i:03d}"
                semantic_chunk.metadata["strategy"] = "hybrid"
                chunks.append(semantic_chunk)
            else:
                # Split large semantic chunk
                sub_chunks = self._split_large_chunk(
                    semantic_chunk.content,
                    f"{document_id}_hybrid_{i:03d}",
                    semantic_chunk.metadata
                )
                chunks.extend(sub_chunks)
        
        # Add overlap between chunks
        if self.overlap_tokens > 0:
            chunks = self._add_overlap(chunks)
        
        return chunks
    
    def _split_large_chunk(self, content: str, base_chunk_id: str, metadata: Dict) -> List[DocumentChunk]:
        """
        Split a large chunk into smaller token-based chunks.
        
        Args:
            content: Chunk content to split
            base_chunk_id: Base chunk identifier
            metadata: Original chunk metadata
            
        Returns:
            List of smaller chunks
        """
        chunks = []
        total_tokens = self.count_tokens(content)
        
        # Split into smaller chunks
        num_sub_chunks = math.ceil(total_tokens / self.target_chunk_size)
        
        for i in range(num_sub_chunks):
            start_token = i * self.target_chunk_size
            end_token = min((i + 1) * self.target_chunk_size, total_tokens)
            
            # Extract sub-chunk content
            sub_content = self._extract_text_by_tokens(content, start_token, end_token)
            
            # Try to break at sentence boundaries
            sub_content = self._adjust_boundaries(sub_content, content, start_token, end_token)
            
            chunk = DocumentChunk(
                content=sub_content,
                chunk_id=f"{base_chunk_id}_sub_{i:02d}",
                start_token=start_token,
                end_token=end_token,
                metadata={
                    **metadata,
                    "strategy": "hybrid",
                    "sub_chunk_index": i,
                    "total_sub_chunks": num_sub_chunks
                }
            )
            chunks.append(chunk)
        
        return chunks
    
    def _extract_text_by_tokens(self, text: str, start_token: int, end_token: int) -> str:
        """
        Extract text between token positions.
        
        Args:
            text: Full text
            start_token: Start token position
            end_token: End token position
            
        Returns:
            Extracted text
        """
        if self.tokenizer:
            # Use tokenizer for precise extraction
            tokens = self.tokenizer.encode(text)
            extracted_tokens = tokens[start_token:end_token]
            return self.tokenizer.decode(extracted_tokens)
        else:
            # Fallback: character-based approximation
            start_char = start_token * 4
            end_char = end_token * 4
            return text[start_char:end_char]
    
    def _adjust_boundaries(self, chunk_content: str, full_content: str, start_token: int, end_token: int) -> str:
        """
        Adjust chunk boundaries to break at sentence or paragraph boundaries.
        
        Args:
            chunk_content: Current chunk content
            full_content: Full document content
            start_token: Start token position
            end_token: End token position
            
        Returns:
            Adjusted chunk content
        """
        # Look for sentence endings near chunk boundaries
        sentence_endings = ['. ', '! ', '? ', '.\n', '!\n', '?\n']
        
        # Try to find better ending boundary
        for ending in sentence_endings:
            if chunk_content.endswith(ending):
                return chunk_content
        
        # If no good ending found, try to extend slightly
        if self.tokenizer:
            tokens = self.tokenizer.encode(full_content)
            # Look for sentence ending within next 50 tokens
            for i in range(end_token, min(end_token + 50, len(tokens))):
                text_so_far = self.tokenizer.decode(tokens[start_token:i])
                for ending in sentence_endings:
                    if text_so_far.endswith(ending):
                        return text_so_far
        
        return chunk_content
    
    def _add_overlap(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        """
        Add overlap between consecutive chunks.
        
        Args:
            chunks: List of chunks
            
        Returns:
            List of chunks with overlap
        """
        if len(chunks) <= 1:
            return chunks
        
        for i in range(len(chunks) - 1):
            current_chunk = chunks[i]
            next_chunk = chunks[i + 1]
            
            # Add overlap from current chunk to next chunk
            if self.overlap_tokens > 0:
                overlap_content = self._extract_text_by_tokens(
                    current_chunk.content,
                    max(0, self.count_tokens(current_chunk.content) - self.overlap_tokens),
                    self.count_tokens(current_chunk.content)
                )
                
                # Prepend overlap to next chunk
                next_chunk.content = overlap_content + "\n\n" + next_chunk.content
                next_chunk.overlap_tokens = self.overlap_tokens
        
        return chunks
    
    def _get_header_level(self, line: str) -> Optional[int]:
        """
        Get the header level from a markdown header line.
        
        Args:
            line: Line to check
            
        Returns:
            Header level (1-6) or None if not a header
        """
        match = re.match(r'^(#{1,6})\s+', line)
        if match:
            return len(match.group(1))
        return None
    
    def chunk_file(self, file_path: Path, output_dir: Optional[Path] = None) -> List[DocumentChunk]:
        """
        Chunk a documentation file and optionally save chunks to disk.
        
        Args:
            file_path: Path to the documentation file
            output_dir: Directory to save chunks (optional)
            
        Returns:
            List of document chunks
        """
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Generate document ID from filename
        document_id = file_path.stem
        
        # Split into chunks
        chunks = self.split_document(content, document_id)
        
        # Save chunks if output directory is provided
        if output_dir:
            output_dir.mkdir(exist_ok=True)
            for chunk in chunks:
                chunk_file = output_dir / f"{chunk.chunk_id}.md"
                with open(chunk_file, 'w', encoding='utf-8') as f:
                    f.write(f"# {chunk.chunk_id}\n\n")
                    f.write(f"**Metadata:** {chunk.metadata}\n\n")
                    f.write(f"**Tokens:** {chunk.start_token}-{chunk.end_token}\n\n")
                    f.write("---\n\n")
                    f.write(chunk.content)
        
        return chunks
    
    def get_chunk_statistics(self, chunks: List[DocumentChunk]) -> Dict:
        """
        Get statistics about the chunks.
        
        Args:
            chunks: List of document chunks
            
        Returns:
            Dictionary with chunk statistics
        """
        if not chunks:
            return {}
        
        token_counts = [self.count_tokens(chunk.content) for chunk in chunks]
        
        return {
            "total_chunks": len(chunks),
            "total_tokens": sum(token_counts),
            "average_tokens": sum(token_counts) / len(token_counts),
            "min_tokens": min(token_counts),
            "max_tokens": max(token_counts),
            "token_distribution": {
                "small": len([t for t in token_counts if t < self.min_chunk_size]),
                "target": len([t for t in token_counts if self.min_chunk_size <= t <= self.max_chunk_size]),
                "large": len([t for t in token_counts if t > self.max_chunk_size])
            }
        }


# Convenience functions
def chunk_documentation_file(
    file_path: Path,
    target_chunk_size: int = 1000,
    min_chunk_size: int = 800,
    max_chunk_size: int = 1200,
    overlap_tokens: int = 100,
    strategy: ChunkStrategy = ChunkStrategy.HYBRID,
    output_dir: Optional[Path] = None
) -> List[DocumentChunk]:
    """
    Convenience function to chunk a single documentation file.
    
    Args:
        file_path: Path to the documentation file
        target_chunk_size: Target number of tokens per chunk
        min_chunk_size: Minimum tokens per chunk
        max_chunk_size: Maximum tokens per chunk
        overlap_tokens: Number of overlapping tokens between chunks
        strategy: Chunking strategy to use
        output_dir: Directory to save chunks (optional)
        
    Returns:
        List of document chunks
    """
    chunker = DocumentationChunker(
        target_chunk_size=target_chunk_size,
        min_chunk_size=min_chunk_size,
        max_chunk_size=max_chunk_size,
        overlap_tokens=overlap_tokens,
        strategy=strategy
    )
    
    return chunker.chunk_file(file_path, output_dir)


def chunk_documentation_directory(
    input_dir: Path,
    output_dir: Path,
    target_chunk_size: int = 1000,
    min_chunk_size: int = 800,
    max_chunk_size: int = 1200,
    overlap_tokens: int = 100,
    strategy: ChunkStrategy = ChunkStrategy.HYBRID
) -> Dict[str, List[DocumentChunk]]:
    """
    Convenience function to chunk all documentation files in a directory.
    
    Args:
        input_dir: Directory containing documentation files
        output_dir: Directory to save chunks
        target_chunk_size: Target number of tokens per chunk
        min_chunk_size: Minimum tokens per chunk
        max_chunk_size: Maximum tokens per chunk
        overlap_tokens: Number of overlapping tokens between chunks
        strategy: Chunking strategy to use
        
    Returns:
        Dictionary mapping file paths to their chunks
    """
    chunker = DocumentationChunker(
        target_chunk_size=target_chunk_size,
        min_chunk_size=min_chunk_size,
        max_chunk_size=max_chunk_size,
        overlap_tokens=overlap_tokens,
        strategy=strategy
    )
    
    results = {}
    
    # Process all markdown files
    for file_path in input_dir.glob("*.md"):
        try:
            chunks = chunker.chunk_file(file_path, output_dir)
            results[str(file_path)] = chunks
            
            # Print statistics
            stats = chunker.get_chunk_statistics(chunks)
            print(f"Chunked {file_path.name}: {stats['total_chunks']} chunks, "
                  f"{stats['total_tokens']} total tokens, "
                  f"avg {stats['average_tokens']:.1f} tokens/chunk")
            
        except Exception as e:
            print(f"Error chunking {file_path}: {e}")
            continue
    
    return results 