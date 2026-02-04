"""
Chat models for ASK and DO modes.
"""

from pydantic import BaseModel
from typing import List, Literal, Optional


class Citation(BaseModel):
    """Knowledge base source citation."""
    score: float
    documentId: str
    sourceUri: Optional[str] = None
    chunkId: Optional[str] = None
    dataSourceId: Optional[str] = None


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
    citations: Optional[List[Citation]] = None
