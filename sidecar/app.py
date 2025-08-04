"""
LLMContext Sidecar FastAPI Server

A dedicated sidecar service for managing tools and retrieving optimized context
from the vector database.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import sys

# Add the parent directory to the path to import llmcontext modules
sys.path.append(str(Path(__file__).parent.parent))

app = FastAPI(
    title="LLMContext Sidecar",
    description="Sidecar service for tool management and context retrieval",
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


# Pydantic models
class ToolInfo(BaseModel):
    name: str
    version: Optional[str] = None


class AddToolRequest(BaseModel):
    tool: str = Field(..., description="Tool name to add")
    version: Optional[str] = Field(None, description="Tool version")


class AddToolResponse(BaseModel):
    success: bool
    message: str
    tool: ToolInfo


class StackResponse(BaseModel):
    tools: List[ToolInfo]
    total: int


class ContextChunk(BaseModel):
    chunk_id: str
    content: str
    tool_name: str
    topic: str
    source_file: str
    similarity_score: float
    metadata: Dict[str, Any]


class ContextResponse(BaseModel):
    chunks: List[ContextChunk]
    total_results: int
    query_info: Dict[str, Any]


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None


# Configuration
CONFIG_FILE = Path(".llmcontext.json")
VECTOR_DB_DIR = Path("chroma_db")
CONTEXT_CACHE_DIR = Path(".llmcontext/context")


def load_config() -> Dict[str, Any]:
    """Load configuration from .llmcontext.json"""
    if not CONFIG_FILE.exists():
        return {"stack": []}
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"stack": []}


def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to .llmcontext.json"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except IOError as e:
        raise HTTPException(status_code=500, detail=f"Failed to save config: {str(e)}")


def parse_tool_string(tool_str: str) -> ToolInfo:
    """Parse tool string (e.g., 'react@18' or 'react') into ToolInfo"""
    if '@' in tool_str:
        name, version = tool_str.split('@', 1)
        return ToolInfo(name=name, version=version)
    else:
        return ToolInfo(name=tool_str)


def format_tool_string(tool: ToolInfo) -> str:
    """Format ToolInfo into tool string"""
    if tool.version:
        return f"{tool.name}@{tool.version}"
    else:
        return tool.name


def save_context_chunks_to_disk(chunks: List[ContextChunk], query_info: Dict[str, Any]) -> None:
    """
    Save context chunks to disk in organized markdown files.
    
    Saves chunks to .llmcontext/context/<tool>/<topic>.md files for manual access.
    """
    try:
        # Ensure context cache directory exists
        CONTEXT_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        
        # Group chunks by tool and topic
        tool_topic_groups = {}
        for chunk in chunks:
            tool_name = chunk.tool_name
            topic = chunk.topic
            
            if tool_name not in tool_topic_groups:
                tool_topic_groups[tool_name] = {}
            
            if topic not in tool_topic_groups[tool_name]:
                tool_topic_groups[tool_name][topic] = []
            
            tool_topic_groups[tool_name][topic].append(chunk)
        
        # Save each tool/topic group to a separate file
        for tool_name, topic_groups in tool_topic_groups.items():
            # Create tool directory
            tool_dir = CONTEXT_CACHE_DIR / tool_name
            tool_dir.mkdir(exist_ok=True)
            
            for topic, topic_chunks in topic_groups.items():
                # Create markdown file for this tool/topic combination
                filename = f"{topic}.md"
                filepath = tool_dir / filename
                
                # Generate markdown content
                markdown_content = generate_context_markdown(topic_chunks, query_info)
                
                # Write to file
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                
                print(f"Saved context chunks to: {filepath}")
    
    except Exception as e:
        # Log error but don't fail the request
        print(f"Warning: Failed to save context chunks to disk: {e}")


def generate_context_markdown(chunks: List[ContextChunk], query_info: Dict[str, Any]) -> str:
    """
    Generate markdown content for context chunks.
    """
    # Header
    tool_name = chunks[0].tool_name if chunks else "Unknown"
    topic = chunks[0].topic if chunks else "Unknown"
    
    markdown_lines = [
        f"# {tool_name.title()} - {topic.title()}",
        "",
        "## Query Information",
        f"- **Query**: {query_info.get('query', 'N/A')}",
        f"- **Search Method**: {query_info.get('search_method', 'N/A')}",
        f"- **Similarity Threshold**: {query_info.get('similarity_threshold', 'N/A')}",
        f"- **Results Found**: {len(chunks)}",
        f"- **Generated**: {query_info.get('timestamp', 'N/A')}",
        "",
        "## Context Chunks",
        ""
    ]
    
    # Add each chunk
    for i, chunk in enumerate(chunks, 1):
        markdown_lines.extend([
            f"### Chunk {i}: {chunk.chunk_id}",
            f"**Similarity Score**: {chunk.similarity_score:.3f}",
            f"**Source File**: {chunk.source_file}",
            "",
            "```markdown",
            chunk.content,
            "```",
            "",
            "---",
            ""
        ])
    
    return "\n".join(markdown_lines)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "LLMContext Sidecar",
        "version": "0.1.0",
        "description": "Sidecar service for tool management and context retrieval",
        "endpoints": {
            "stack": "/stack",
            "add_tool": "/add-tool",
            "context": "/context",
            "health": "/health",
            "docs": "/docs",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "llmcontext-sidecar",
        "version": "0.1.0",
    }


@app.get("/stack", response_model=StackResponse)
async def get_stack():
    """
    Get the current stack of selected tools.
    """
    try:
        config = load_config()
        tools = []
        
        for tool_str in config.get("stack", []):
            tool_info = parse_tool_string(tool_str)
            tools.append(tool_info)
        
        return StackResponse(
            tools=tools,
            total=len(tools)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/add-tool", response_model=AddToolResponse)
async def add_tool(request: AddToolRequest):
    """
    Add a tool to the stack.
    """
    try:
        config = load_config()
        stack = config.get("stack", [])
        
        # Format the tool string
        if request.version:
            tool_str = f"{request.tool}@{request.version}"
        else:
            tool_str = request.tool
        
        # Check if tool already exists
        existing_tools = [parse_tool_string(t) for t in stack]
        for existing_tool in existing_tools:
            if existing_tool.name == request.tool:
                # Update version if different
                if existing_tool.version != request.version:
                    stack.remove(format_tool_string(existing_tool))
                    stack.append(tool_str)
                    save_config(config)
                    return AddToolResponse(
                        success=True,
                        message=f"Updated {request.tool} version to {request.version or 'latest'}",
                        tool=ToolInfo(name=request.tool, version=request.version)
                    )
                else:
                    return AddToolResponse(
                        success=True,
                        message=f"{request.tool} already exists in stack",
                        tool=ToolInfo(name=request.tool, version=request.version)
                    )
        
        # Add new tool
        stack.append(tool_str)
        config["stack"] = stack
        save_config(config)
        
        return AddToolResponse(
            success=True,
            message=f"Added {request.tool} to stack",
            tool=ToolInfo(name=request.tool, version=request.version)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/context", response_model=ContextResponse)
async def get_context(
    tool: str = Query(..., description="Tool/framework name to search in"),
    topic: str = Query(..., description="Topic to search in"),
    n_results: int = Query(10, description="Number of results to return", ge=1, le=100),
    similarity_threshold: float = Query(0.5, description="Minimum similarity score", ge=0.0, le=1.0)
):
    """
    Retrieve optimized context chunks from the vector database.
    
    This endpoint searches the ChromaDB vector store for relevant documentation chunks
    based on tool and topic parameters.
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
        if not VECTOR_DB_DIR.exists():
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
                persist_directory=VECTOR_DB_DIR,
                collection_name="llmcontext_docs",
                api_key=api_key
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize vector database: {str(e)}"
            )
        
        # Get documents for specific tool and topic
        search_results = db.get_documents_by_topic(topic, n_results)
        
        # Filter by tool
        search_results = [
            result for result in search_results 
            if result.tool_name.lower() == tool.lower()
        ]
        
        if not search_results:
            # Try semantic search as fallback
            query = f"{tool} {topic}"
            search_results = db.search_by_text(
                query=query,
                n_results=n_results,
                filter_metadata={"tool_name": tool}
            )
            
            # Filter by similarity threshold
            search_results = [
                result for result in search_results 
                if result.similarity_score >= similarity_threshold
            ]
        
        if not search_results:
            # Get available tools and topics for better error message
            available_tools = db.get_tools()
            available_topics = db.get_topics()
            
            raise HTTPException(
                status_code=404,
                detail={
                    "message": f"No matching documents found for tool '{tool}' and topic '{topic}'",
                    "available_tools": available_tools,
                    "available_topics": available_topics,
                    "suggestions": [
                        f"Try searching for tool '{t}' instead" for t in available_tools if t.lower() != tool.lower()
                    ] + [
                        f"Try searching for topic '{t}' instead" for t in available_topics if t.lower() != topic.lower()
                    ]
                }
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
            "n_results": n_results,
            "similarity_threshold": similarity_threshold,
            "results_returned": len(chunks),
            "search_method": "direct" if len(chunks) == len(search_results) else "semantic",
            "timestamp": datetime.now().isoformat()
        }
        
        # Save context chunks to disk
        save_context_chunks_to_disk(chunks, query_info)
        
        return ContextResponse(
            chunks=chunks,
            total_results=len(chunks),
            query_info=query_info
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/context/vector", response_model=ContextResponse)
async def get_vector_context(
    query: str = Query(..., description="Search query/question"),
    n_results: int = Query(10, description="Number of results to return", ge=1, le=100),
    similarity_threshold: float = Query(0.5, description="Minimum similarity score", ge=0.0, le=1.0)
):
    """
    Retrieve optimized context chunks from the vector database using universal search.
    
    This endpoint performs semantic search across all tools and topics to find
    the most relevant documentation chunks for the given query.
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
        if not VECTOR_DB_DIR.exists():
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
                persist_directory=VECTOR_DB_DIR,
                collection_name="llmcontext_docs",
                api_key=api_key
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize vector database: {str(e)}"
            )
        
        # Perform semantic search across all tools and topics
        search_results = db.search_by_text(
            query=query,
            n_results=n_results,
            similarity_threshold=similarity_threshold
        )
        
        if not search_results:
            # Get available tools and topics for better error message
            available_tools = db.get_tools()
            available_topics = db.get_topics()
            
            raise HTTPException(
                status_code=404,
                detail={
                    "message": f"No matching documents found for query '{query}'",
                    "available_tools": available_tools,
                    "available_topics": available_topics,
                    "suggestions": [
                        "Try rephrasing your query",
                        "Try using more specific terms",
                        "Lower the similarity threshold"
                    ]
                }
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
            "query": query,
            "n_results": n_results,
            "similarity_threshold": similarity_threshold,
            "results_returned": len(chunks),
            "search_method": "semantic",
            "tools_found": list(set(chunk.tool_name for chunk in chunks)),
            "topics_found": list(set(chunk.topic for chunk in chunks)),
            "timestamp": datetime.now().isoformat()
        }
        
        # Save context chunks to disk
        save_context_chunks_to_disk(chunks, query_info)
        
        return ContextResponse(
            chunks=chunks,
            total_results=len(chunks),
            query_info=query_info
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tools")
async def list_available_tools():
    """
    List all available tools in the vector database.
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
        if not VECTOR_DB_DIR.exists():
            return {"tools": [], "message": "Vector database not found"}
        
        # Initialize vector database
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="OpenAI API key not found. Set OPENAI_API_KEY environment variable."
            )
        
        try:
            db = VectorDatabase(
                persist_directory=VECTOR_DB_DIR,
                collection_name="llmcontext_docs",
                api_key=api_key
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize vector database: {str(e)}"
            )
        
        # Get available tools and their topics
        tools = db.get_tools()
        tool_details = {}
        
        for tool in tools:
            topics = db.get_topics(tool)
            tool_details[tool] = {
                "topics": topics,
                "topic_count": len(topics)
            }
        
        return {
            "tools": tool_details,
            "total_tools": len(tools)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/topics")
async def list_available_topics(tool: Optional[str] = Query(None, description="Filter topics by tool")):
    """
    List all available topics in the vector database.
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
        if not VECTOR_DB_DIR.exists():
            return {"topics": [], "message": "Vector database not found"}
        
        # Initialize vector database
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="OpenAI API key not found. Set OPENAI_API_KEY environment variable."
            )
        
        try:
            db = VectorDatabase(
                persist_directory=VECTOR_DB_DIR,
                collection_name="llmcontext_docs",
                api_key=api_key
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize vector database: {str(e)}"
            )
        
        # Get available topics
        topics = db.get_topics(tool)
        
        return {
            "topics": topics,
            "total_topics": len(topics),
            "filtered_by_tool": tool is not None
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001) 