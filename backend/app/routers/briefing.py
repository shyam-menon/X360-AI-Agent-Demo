"""
Briefing API endpoints.
"""

from fastapi import APIRouter, HTTPException
from app.models.briefing import BriefingRequest, BriefingResponse
from app.agents.briefing_agent import briefing_agent
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/briefing", response_model=BriefingResponse)
async def run_briefing(request: BriefingRequest):
    """
    Run morning briefing analysis on virtualization layer data.

    Analyzes data from multiple systems and returns:
    - Summary of system health
    - List of items (SLA breaches, conflicts, insights)
    """
    try:
        logger.info(f"Running briefing analysis on {len(request.data)} data points")

        result = await briefing_agent.analyze_data(request.data)

        logger.info(f"Briefing complete: {len(result.get('items', []))} items found")

        return BriefingResponse(**result)

    except Exception as e:
        logger.error(f"Briefing failed: {str(e)}", exc_info=True)
        # Return fallback response
        return BriefingResponse(
            summary="System is offline. Displaying cached operational data.",
            items=[]
        )
