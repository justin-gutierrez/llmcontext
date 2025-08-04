"""
Tests for API functionality.
"""

import pytest
from fastapi.testclient import TestClient
from llmcontext.api import app


@pytest.fixture
def client():
    """Create a test client for the API."""
    return TestClient(app)


def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "LLMContext API"
    assert data["version"] == "0.1.0"


def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "llmcontext"


def test_frameworks_endpoint(client):
    """Test the frameworks endpoint."""
    response = client.get("/frameworks")
    assert response.status_code == 200
    data = response.json()
    assert "frameworks" in data


def test_docs_endpoint(client):
    """Test the docs endpoint."""
    response = client.get("/docs")
    assert response.status_code == 200
    data = response.json()
    assert "documentation_files" in data


def test_process_endpoint(client):
    """Test the process endpoint."""
    request_data = {
        "codebase_path": "/tmp/test",
        "output_dir": "docs"
    }
    response = client.post("/process", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert "frameworks" in data
    assert "documentation_files" in data
    assert "status" in data


def test_context_endpoint(client):
    """Test the context endpoint."""
    request_data = {
        "query": "fastapi",
        "limit": 5
    }
    response = client.post("/context", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert "context" in data
    assert "sources" in data
    assert "total_results" in data 