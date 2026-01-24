"""
Unit tests for Strands agents.
"""

import pytest
from app.agents.briefing_agent import briefing_agent
from app.agents.chat_agent import chat_agent
from app.agents.action_agent import action_agent


@pytest.mark.asyncio
async def test_briefing_agent():
    """Test briefing agent analysis."""
    sample_data = [
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

    result = await briefing_agent.analyze_data(sample_data)

    assert "summary" in result
    assert "items" in result
    assert isinstance(result["items"], list)


@pytest.mark.asyncio
async def test_chat_agent():
    """Test chat agent interaction."""
    context = {
        "data": [],
        "briefing": {}
    }

    result = await chat_agent.chat(
        message="What tickets are open?",
        history=[],
        context=context
    )

    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_action_agent():
    """Test action agent execution."""
    context = {
        "data": []
    }

    result = await action_agent.execute(
        command="Update ticket SN-001 to In Progress",
        context=context
    )

    assert isinstance(result, str)
    assert len(result) > 0
