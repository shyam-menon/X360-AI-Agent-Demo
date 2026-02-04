"""
Chat API endpoints.
"""

from fastapi import APIRouter, HTTPException
from app.models.chat import ChatRequest, ChatResponse
from app.agents.chat_agent import chat_agent
from app.agents.action_agent import action_agent
import logging
import time

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def send_chat_message(request: ChatRequest):
    """
    Send a chat message to the appropriate agent (ASK or DO mode).

    - ASK mode: Uses chat agent for Q&A
    - DO mode: Uses action agent for executing commands
    """
    try:
        logger.info(f"Chat request - Mode: {request.mode}, Message: {request.message[:50]}...")

        start_time = time.time()

        if request.mode == "DO":
            # Use action agent for DO mode
            response_text = await action_agent.execute(request.message, request.context or {})
            duration = time.time() - start_time
            logger.info(f"Chat response generated in {duration:.2f}s")

            return ChatResponse(
                response=response_text,
                timestamp=int(time.time() * 1000),
                citations=None  # DO mode doesn't use KB
            )
        else:
            # Use chat agent for ASK mode
            # Convert Pydantic models to dicts for the agent
            history_dicts = [msg.model_dump() for msg in request.history]
            result = await chat_agent.chat(
                message=request.message,
                history=history_dicts,
                context=request.context or {}
            )

            duration = time.time() - start_time
            logger.info(f"Chat response generated in {duration:.2f}s")

            return ChatResponse(
                response=result["response"],
                timestamp=int(time.time() * 1000),
                citations=result.get("citations")
            )

    except Exception as e:
        logger.error(f"Chat failed: {str(e)}", exc_info=True)
        return ChatResponse(
            response="I am having trouble connecting to the X360 core. Please check your connection.",
            timestamp=int(time.time() * 1000),
            citations=None
        )
