"""
Integration tests for FastAPI endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"


def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_briefing_endpoint():
    """Test briefing endpoint."""
    payload = {
        "data": [
            {
                "id": "SN-001",
                "customer": "Acme Corp",
                "title": "Server Down",
                "status": "Open",
                "priority": "Critical",
                "createdDate": "2026-01-20T10:00:00Z",
                "dueDate": "2026-01-21T10:00:00Z",
                "source": "ServiceNow",
                "assignee": "John Doe"
            }
        ]
    }

    response = client.post("/api/v1/briefing", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "items" in data


def test_chat_endpoint():
    """Test chat endpoint."""
    payload = {
        "message": "What tickets are open?",
        "history": [],
        "mode": "ASK",
        "context": {
            "data": [],
            "briefing": {}
        }
    }

    response = client.post("/api/v1/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "timestamp" in data
