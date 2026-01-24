"""
Briefing models for morning briefing analysis.
"""

from pydantic import BaseModel
from typing import List, Literal, Optional


class BriefingItem(BaseModel):
    """Individual briefing item (SLA breach, conflict, or insight)."""

    id: str
    type: Literal["SLA_BREACH", "DATA_CONFLICT", "INSIGHT"]
    title: str
    description: str
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    relatedTicketIds: List[str]
    suggestedAction: Optional[str] = None


class BriefingRequest(BaseModel):
    """Request payload for briefing analysis."""

    data: List[dict]  # RAW_CHAOTIC_DATA from frontend


class BriefingResponse(BaseModel):
    """Response from briefing analysis."""

    summary: str
    items: List[BriefingItem]
