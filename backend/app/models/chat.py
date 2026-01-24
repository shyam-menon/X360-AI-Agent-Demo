"""
Chat models for ASK and DO modes.
"""

from pydantic import BaseModel
from typing import List, Literal, Optional


class ChatMessage(BaseModel):
    """Individual chat message in conversation history."""

    role: Literal["user", "model"]
    content: str
    timestamp: int
    isAction: Optional[bool] = False


class ChatRequest(BaseModel):
    """Request payload for chat interaction."""

    message: str
    history: List[ChatMessage]
    mode: Literal["ASK", "DO"]
    context: Optional[dict] = None  # Contains data and briefing


class ChatResponse(BaseModel):
    """Response from chat agent."""

    response: str
    timestamp: int
