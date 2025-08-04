"""
Vector Database Module

This module provides ChromaDB integration for storing vector embeddings and metadata,
with basic retrieval functionality by keyword or topic.
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
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Represents a search result from the vector database."""
    chunk_id: str
    content: str
    tool_name: str
    topic: str
    source_file: str
    similarity_score: float
    metadata: Dict[str, Any]


@dataclass
class CollectionInfo:
    """Represents information about a ChromaDB collection."""
    name: str
    count: int
    metadata: Dict[str, Any]


class VectorDatabase:
    """ChromaDB-based vector database for storing and retrieving embeddings."""
    
    def __init__(
        self,
        persist_directory: Path = Path("chroma_db"),
        collection_name: str = "llmcontext_docs",
        embedding_function: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize the vector database.
        
        Args:
            persist_directory: Directory to persist ChromaDB data
            collection_name: Name of the collection to use
            embedding_function: Embedding function to use (default: OpenAI)
            api_key: OpenAI API key for embedding function
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        # Create persist directory
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Set up embedding function
        if embedding_function == "openai" or embedding_function is None:
            if not self.api_key:
                raise ValueError("OpenAI API key is required for OpenAI embedding function")
            self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
                api_key=self.api_key,
                model_name="text-embedding-3-large"
            )
        else:
            # Use default sentence transformers
            self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction()
        
        # Get or create collection
        self.collection = self._get_or_create_collection()
        
        logger.info(f"Initialized VectorDatabase with collection: {collection_name}")
        logger.info(f"Persist directory: {persist_directory}")
    
    def _get_or_create_collection(self) -> chromadb.Collection:
        """Get existing collection or create a new one."""
        try:
            # Try to get existing collection
            collection = self.client.get_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function
            )
            logger.info(f"Using existing collection: {self.collection_name}")
            return collection
        except Exception:
            # Create new collection
            collection = self.client.create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function,
                metadata={
                    "description": "LLMContext documentation embeddings",
                    "created_at": datetime.now().isoformat(),
                    "embedding_model": "text-embedding-3-large"
                }
            )
            logger.info(f"Created new collection: {self.collection_name}")
            return collection
    
    def add_embeddings_from_file(
        self,
        embeddings_file: Path,
        batch_size: int = 100
    ) -> Dict[str, Any]:
        """
        Add embeddings from a JSON embeddings file.
        
        Args:
            embeddings_file: Path to JSON embeddings file
            batch_size: Number of embeddings to add in a batch
            
        Returns:
            Dictionary with operation results
        """
        logger.info(f"Adding embeddings from file: {embeddings_file}")
        
        if not embeddings_file.exists():
            raise FileNotFoundError(f"Embeddings file not found: {embeddings_file}")
        
        with open(embeddings_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        batch_metadata = data.get('batch_metadata', {})
        embeddings_data = data.get('embeddings', [])
        
        if not embeddings_data:
            raise ValueError(f"No embeddings found in {embeddings_file}")
        
        # Prepare data for ChromaDB
        ids = []
        embeddings = []
        documents = []
        metadatas = []
        
        for embedding_data in embeddings_data:
            chunk_id = embedding_data['chunk_id']
            content = embedding_data['content']
            embedding = embedding_data['embedding']
            metadata = embedding_data['metadata']
            
            # Add batch metadata to individual metadata
            full_metadata = {
                **metadata,
                'batch_processed_at': batch_metadata.get('processed_at'),
                'batch_model': batch_metadata.get('model'),
                'batch_embedding_dimensions': batch_metadata.get('embedding_dimensions')
            }
            
            ids.append(chunk_id)
            embeddings.append(embedding)
            documents.append(content)
            metadatas.append(full_metadata)
        
        # Add embeddings in batches
        total_added = 0
        for i in range(0, len(ids), batch_size):
            batch_ids = ids[i:i + batch_size]
            batch_embeddings = embeddings[i:i + batch_size]
            batch_documents = documents[i:i + batch_size]
            batch_metadatas = metadatas[i:i + batch_size]
            
            try:
                self.collection.add(
                    ids=batch_ids,
                    embeddings=batch_embeddings,
                    documents=batch_documents,
                    metadatas=batch_metadatas
                )
                total_added += len(batch_ids)
                logger.info(f"Added batch {i//batch_size + 1}: {len(batch_ids)} embeddings")
                
            except Exception as e:
                logger.error(f"Error adding batch {i//batch_size + 1}: {e}")
                continue
        
        return {
            'file': str(embeddings_file),
            'total_embeddings': len(embeddings_data),
            'added_embeddings': total_added,
            'batch_metadata': batch_metadata
        }
    
    def add_embeddings_from_directory(
        self,
        embeddings_dir: Path,
        tools: Optional[List[str]] = None,
        topics: Optional[List[str]] = None,
        batch_size: int = 100
    ) -> Dict[str, Any]:
        """
        Add embeddings from all JSON files in a directory.
        
        Args:
            embeddings_dir: Directory containing embeddings files
            tools: Optional list of tools to process
            topics: Optional list of topics to process
            batch_size: Number of embeddings to add in a batch
            
        Returns:
            Dictionary with operation results
        """
        logger.info(f"Adding embeddings from directory: {embeddings_dir}")
        
        if not embeddings_dir.exists():
            raise FileNotFoundError(f"Embeddings directory not found: {embeddings_dir}")
        
        results = []
        total_added = 0
        
        # Find all JSON embeddings files
        for tool_dir in embeddings_dir.iterdir():
            if not tool_dir.is_dir():
                continue
            
            tool_name = tool_dir.name
            
            # Filter by tools if specified
            if tools and tool_name not in tools:
                continue
            
            logger.info(f"Processing tool: {tool_name}")
            
            for json_file in tool_dir.glob("*_embeddings.json"):
                topic_name = json_file.stem.replace("_embeddings", "")
                
                # Filter by topics if specified
                if topics and topic_name not in topics:
                    continue
                
                try:
                    result = self.add_embeddings_from_file(json_file, batch_size)
                    results.append(result)
                    total_added += result['added_embeddings']
                    
                except Exception as e:
                    logger.error(f"Error processing {json_file}: {e}")
                    continue
        
        return {
            'directory': str(embeddings_dir),
            'files_processed': len(results),
            'total_added': total_added,
            'results': results
        }
    
    def search_by_text(
        self,
        query: str,
        n_results: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Search for similar documents by text query.
        
        Args:
            query: Text query to search for
            n_results: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of SearchResult objects
        """
        logger.info(f"Searching for: '{query}' (n_results={n_results})")
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=filter_metadata
            )
            
            search_results = []
            for i in range(len(results['ids'][0])):
                chunk_id = results['ids'][0][i]
                content = results['documents'][0][i]
                metadata = results['metadatas'][0][i]
                distance = results['distances'][0][i]
                
                # Convert distance to similarity score (ChromaDB uses L2 distance)
                similarity_score = 1.0 / (1.0 + distance)
                
                search_result = SearchResult(
                    chunk_id=chunk_id,
                    content=content,
                    tool_name=metadata.get('tool_name', 'unknown'),
                    topic=metadata.get('topic', 'unknown'),
                    source_file=metadata.get('source_file', 'unknown'),
                    similarity_score=similarity_score,
                    metadata=metadata
                )
                search_results.append(search_result)
            
            return search_results
            
        except Exception as e:
            logger.error(f"Error during search: {e}")
            return []
    
    def search_by_tool(
        self,
        tool_name: str,
        query: str = "",
        n_results: int = 10
    ) -> List[SearchResult]:
        """
        Search for documents within a specific tool.
        
        Args:
            tool_name: Name of the tool to search in
            query: Optional text query
            n_results: Number of results to return
            
        Returns:
            List of SearchResult objects
        """
        filter_metadata = {"tool_name": tool_name}
        
        if query:
            return self.search_by_text(query, n_results, filter_metadata)
        else:
            # Get all documents for the tool
            return self.get_documents_by_tool(tool_name, n_results)
    
    def search_by_topic(
        self,
        topic: str,
        query: str = "",
        n_results: int = 10
    ) -> List[SearchResult]:
        """
        Search for documents within a specific topic.
        
        Args:
            topic: Name of the topic to search in
            query: Optional text query
            n_results: Number of results to return
            
        Returns:
            List of SearchResult objects
        """
        filter_metadata = {"topic": topic}
        
        if query:
            return self.search_by_text(query, n_results, filter_metadata)
        else:
            # Get all documents for the topic
            return self.get_documents_by_topic(topic, n_results)
    
    def get_documents_by_tool(
        self,
        tool_name: str,
        n_results: int = 100
    ) -> List[SearchResult]:
        """
        Get all documents for a specific tool.
        
        Args:
            tool_name: Name of the tool
            n_results: Maximum number of results to return
            
        Returns:
            List of SearchResult objects
        """
        try:
            results = self.collection.get(
                where={"tool_name": tool_name},
                limit=n_results
            )
            
            search_results = []
            for i in range(len(results['ids'])):
                chunk_id = results['ids'][i]
                content = results['documents'][i]
                metadata = results['metadatas'][i]
                
                search_result = SearchResult(
                    chunk_id=chunk_id,
                    content=content,
                    tool_name=metadata.get('tool_name', 'unknown'),
                    topic=metadata.get('topic', 'unknown'),
                    source_file=metadata.get('source_file', 'unknown'),
                    similarity_score=1.0,  # No similarity score for direct retrieval
                    metadata=metadata
                )
                search_results.append(search_result)
            
            return search_results
            
        except Exception as e:
            logger.error(f"Error getting documents for tool {tool_name}: {e}")
            return []
    
    def get_documents_by_topic(
        self,
        topic: str,
        n_results: int = 100
    ) -> List[SearchResult]:
        """
        Get all documents for a specific topic.
        
        Args:
            topic: Name of the topic
            n_results: Maximum number of results to return
            
        Returns:
            List of SearchResult objects
        """
        try:
            results = self.collection.get(
                where={"topic": topic},
                limit=n_results
            )
            
            search_results = []
            for i in range(len(results['ids'])):
                chunk_id = results['ids'][i]
                content = results['documents'][i]
                metadata = results['metadatas'][i]
                
                search_result = SearchResult(
                    chunk_id=chunk_id,
                    content=content,
                    tool_name=metadata.get('tool_name', 'unknown'),
                    topic=metadata.get('topic', 'unknown'),
                    source_file=metadata.get('source_file', 'unknown'),
                    similarity_score=1.0,  # No similarity score for direct retrieval
                    metadata=metadata
                )
                search_results.append(search_result)
            
            return search_results
            
        except Exception as e:
            logger.error(f"Error getting documents for topic {topic}: {e}")
            return []
    
    def get_collection_info(self) -> CollectionInfo:
        """
        Get information about the collection.
        
        Returns:
            CollectionInfo object
        """
        try:
            count = self.collection.count()
            metadata = self.collection.metadata or {}
            
            return CollectionInfo(
                name=self.collection_name,
                count=count,
                metadata=metadata
            )
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return CollectionInfo(
                name=self.collection_name,
                count=0,
                metadata={}
            )
    
    def get_tools(self) -> List[str]:
        """
        Get list of all tools in the database.
        
        Returns:
            List of tool names
        """
        try:
            results = self.collection.get(include=['metadatas'])
            tools = set()
            
            for metadata in results['metadatas']:
                if metadata and 'tool_name' in metadata:
                    tools.add(metadata['tool_name'])
            
            return sorted(list(tools))
            
        except Exception as e:
            logger.error(f"Error getting tools: {e}")
            return []
    
    def get_topics(self, tool_name: Optional[str] = None) -> List[str]:
        """
        Get list of all topics in the database.
        
        Args:
            tool_name: Optional tool name to filter by
            
        Returns:
            List of topic names
        """
        try:
            where_filter = {"tool_name": tool_name} if tool_name else None
            results = self.collection.get(include=['metadatas'], where=where_filter)
            topics = set()
            
            for metadata in results['metadatas']:
                if metadata and 'topic' in metadata:
                    topics.add(metadata['topic'])
            
            return sorted(list(topics))
            
        except Exception as e:
            logger.error(f"Error getting topics: {e}")
            return []
    
    def delete_documents(self, filter_metadata: Dict[str, Any]) -> int:
        """
        Delete documents matching the filter criteria.
        
        Args:
            filter_metadata: Metadata filter for documents to delete
            
        Returns:
            Number of documents deleted
        """
        try:
            # Get documents to delete
            results = self.collection.get(where=filter_metadata)
            ids_to_delete = results['ids']
            
            if ids_to_delete:
                self.collection.delete(ids=ids_to_delete)
                logger.info(f"Deleted {len(ids_to_delete)} documents")
                return len(ids_to_delete)
            else:
                logger.info("No documents found matching filter criteria")
                return 0
                
        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            return 0
    
    def reset_collection(self) -> bool:
        """
        Reset the collection (delete all documents).
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.delete_collection(self.collection_name)
            self.collection = self._get_or_create_collection()
            logger.info(f"Reset collection: {self.collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting collection: {e}")
            return False


# Convenience functions
def create_vector_database(
    persist_directory: Path = Path("chroma_db"),
    collection_name: str = "llmcontext_docs",
    api_key: Optional[str] = None
) -> VectorDatabase:
    """
    Create a new vector database instance.
    
    Args:
        persist_directory: Directory to persist ChromaDB data
        collection_name: Name of the collection
        api_key: OpenAI API key
        
    Returns:
        VectorDatabase instance
    """
    return VectorDatabase(
        persist_directory=persist_directory,
        collection_name=collection_name,
        api_key=api_key
    )


def add_embeddings_to_database(
    embeddings_dir: Path,
    persist_directory: Path = Path("chroma_db"),
    collection_name: str = "llmcontext_docs",
    api_key: Optional[str] = None,
    tools: Optional[List[str]] = None,
    topics: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Convenience function to add embeddings to the database.
    
    Args:
        embeddings_dir: Directory containing embeddings files
        persist_directory: ChromaDB persist directory
        collection_name: Collection name
        api_key: OpenAI API key
        tools: Optional list of tools to process
        topics: Optional list of topics to process
        
    Returns:
        Operation results
    """
    db = VectorDatabase(
        persist_directory=persist_directory,
        collection_name=collection_name,
        api_key=api_key
    )
    
    return db.add_embeddings_from_directory(embeddings_dir, tools, topics) 