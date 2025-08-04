"""
FastAPI sidecar server for LLMContext.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from pathlib import Path

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