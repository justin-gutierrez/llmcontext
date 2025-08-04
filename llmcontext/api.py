"""
FastAPI sidecar server for LLMContext.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from pathlib import Path
import os

app = FastAPI(
    title="LLMContext API",
    description="Universal sidecar service for framework detection and documentation optimization",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for API requests/responses
class ProcessRequest(BaseModel):
    codebase_path: str
    output_dir: Optional[str] = "docs"


class FrameworkInfo(BaseModel):
    name: str
    version: Optional[str]
    confidence: float
    files: List[str]


class ProcessResponse(BaseModel):
    frameworks: List[FrameworkInfo]
    documentation_files: List[str]
    status: str


class ContextRequest(BaseModel):
    query: str
    frameworks: Optional[List[str]] = None
    limit: Optional[int] = 10


class ContextResponse(BaseModel):
    context: List[Dict[str, Any]]
    sources: List[str]
    total_results: int


class ContextChunk(BaseModel):
    chunk_id: str
    content: str
    tool_name: str
    topic: str
    source_file: str
    similarity_score: float
    metadata: Dict[str, Any]


class VectorContextResponse(BaseModel):
    chunks: List[ContextChunk]
    total_results: int
    query_info: Dict[str, Any]


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "LLMContext API",
        "version": "0.1.0",
        "description": "Universal sidecar service for framework detection and documentation optimization",
        "endpoints": {
            "health": "/health",
            "process": "/process",
            "context": "/context",
            "vector_context": "/context/vector",
            "frameworks": "/frameworks",
            "docs": "/docs",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "llmcontext",
        "version": "0.1.0",
    }


@app.post("/process", response_model=ProcessResponse)
async def process_codebase(request: ProcessRequest):
    """
    Process a codebase to detect frameworks and collect documentation.
    """
    try:
        codebase_path = Path(request.codebase_path)
        if not codebase_path.exists():
            raise HTTPException(status_code=404, detail="Codebase path not found")
        
        # TODO: Implement actual framework detection and documentation collection
        # For now, return mock data
        frameworks = [
            FrameworkInfo(
                name="fastapi",
                version="0.104.0",
                confidence=0.95,
                files=["main.py", "api.py"]
            ),
            FrameworkInfo(
                name="click",
                version="8.1.0",
                confidence=0.90,
                files=["cli.py"]
            )
        ]
        
        return ProcessResponse(
            frameworks=frameworks,
            documentation_files=["docs/fastapi.md", "docs/click.md"],
            status="completed"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/context", response_model=ContextResponse)
async def get_context(request: ContextRequest):
    """
    Retrieve optimized context based on a query.
    """
    try:
        # TODO: Implement actual context retrieval with RAG
        # For now, return mock data
        context = [
            {
                "content": "FastAPI is a modern, fast web framework for building APIs with Python.",
                "source": "docs/fastapi.md",
                "relevance": 0.95,
                "tags": ["web", "api", "python"]
            },
            {
                "content": "Click is a Python package for creating beautiful command line interfaces.",
                "source": "docs/click.md",
                "relevance": 0.85,
                "tags": ["cli", "python"]
            }
        ]
        
        return ContextResponse(
            context=context[:request.limit],
            sources=["docs/fastapi.md", "docs/click.md"],
            total_results=len(context)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/context/vector", response_model=VectorContextResponse)
async def get_vector_context(
    tool: Optional[str] = Query(None, description="Tool/framework name to search in"),
    topic: Optional[str] = Query(None, description="Topic to search in"),
    query: Optional[str] = Query(None, description="Text query for semantic search"),
    n_results: int = Query(10, description="Number of results to return", ge=1, le=100),
    similarity_threshold: float = Query(0.5, description="Minimum similarity score", ge=0.0, le=1.0)
):
    """
    Retrieve context chunks from the vector database.
    
    This endpoint searches the ChromaDB vector store for relevant documentation chunks
    based on tool, topic, and optional text query parameters.
    """
    try:
        # Import vector database module
        try:
            from llmcontext.core.vectordb import VectorDatabase
        except ImportError as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Vector database module not available: {str(e)}"
            )
        
        # Check if vector database exists
        persist_dir = Path("chroma_db")
        if not persist_dir.exists():
            raise HTTPException(
                status_code=404,
                detail="Vector database not found. Please run 'llmcontext vectordb add' first."
            )
        
        # Initialize vector database
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="OpenAI API key not found. Set OPENAI_API_KEY environment variable."
            )
        
        try:
            db = VectorDatabase(
                persist_directory=persist_dir,
                collection_name="llmcontext_docs",
                api_key=api_key
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize vector database: {str(e)}"
            )
        
        # Determine search strategy based on parameters
        if query:
            # Semantic search with optional filters
            filter_metadata = {}
            if tool:
                filter_metadata['tool_name'] = tool
            if topic:
                filter_metadata['topic'] = topic
            
            search_results = db.search_by_text(
                query=query,
                n_results=n_results,
                filter_metadata=filter_metadata if filter_metadata else None
            )
            
            # Filter by similarity threshold
            search_results = [
                result for result in search_results 
                if result.similarity_score >= similarity_threshold
            ]
            
        elif tool and topic:
            # Get documents for specific tool and topic
            search_results = db.get_documents_by_topic(topic, n_results)
            # Filter by tool
            search_results = [
                result for result in search_results 
                if result.tool_name == tool
            ]
            
        elif tool:
            # Get documents for specific tool
            search_results = db.get_documents_by_tool(tool, n_results)
            
        elif topic:
            # Get documents for specific topic
            search_results = db.get_documents_by_topic(topic, n_results)
            
        else:
            # Get collection info to show available data
            info = db.get_collection_info()
            if info.count == 0:
                raise HTTPException(
                    status_code=404,
                    detail="No documents found in vector database. Please add embeddings first."
                )
            
            # Get all available tools and topics
            tools = db.get_tools()
            topics = db.get_topics()
            
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Please specify at least one of: tool, topic, or query",
                    "available_tools": tools,
                    "available_topics": topics,
                    "total_documents": info.count
                }
            )
        
        if not search_results:
            raise HTTPException(
                status_code=404,
                detail="No matching documents found for the specified criteria."
            )
        
        # Convert search results to response format
        chunks = []
        for result in search_results:
            chunk = ContextChunk(
                chunk_id=result.chunk_id,
                content=result.content,
                tool_name=result.tool_name,
                topic=result.topic,
                source_file=result.source_file,
                similarity_score=result.similarity_score,
                metadata=result.metadata
            )
            chunks.append(chunk)
        
        # Prepare query information
        query_info = {
            "tool": tool,
            "topic": topic,
            "query": query,
            "n_results": n_results,
            "similarity_threshold": similarity_threshold,
            "results_returned": len(chunks)
        }
        
        return VectorContextResponse(
            chunks=chunks,
            total_results=len(chunks),
            query_info=query_info
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/frameworks")
async def list_frameworks():
    """
    List all detected frameworks in the current codebase.
    """
    # TODO: Implement actual framework listing
    return {
        "frameworks": [
            {"name": "fastapi", "version": "0.104.0", "confidence": 0.95},
            {"name": "click", "version": "8.1.0", "confidence": 0.90},
        ]
    }


@app.get("/docs")
async def list_documentation():
    """
    List all available documentation files.
    """
    docs_dir = Path("docs")
    if not docs_dir.exists():
        return {"documentation_files": []}
    
    files = [f.name for f in docs_dir.glob("*.md")]
    return {"documentation_files": files}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000) 