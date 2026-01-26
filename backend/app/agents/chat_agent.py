"""
Chat Agent - Handles ASK mode interactions.
"""

from strands import Agent
from strands.tools import tool
from strands_tools import retrieve
from typing import List, Dict
import os
import json

from app.config import settings

# Set environment variables for the retrieve tool before it's used
os.environ.setdefault("KNOWLEDGE_BASE_ID", settings.knowledge_base_id)
os.environ.setdefault("AWS_REGION", settings.knowledge_base_region)
os.environ.setdefault("MIN_SCORE", str(settings.knowledge_base_min_score))

SYSTEM_INSTRUCTION_CHAT = """
You are an AI agent assistant for X360, a virtualized ops platform.
You help operators understand tickets, data conflicts, system insights, and provide knowledge from documentation.

## Available Tools:

### query_tickets
Use for questions about specific ticket data in the current dataset:
- Finding tickets by ID, status, priority, or customer
- Data conflicts between systems
- SLA breaches related to specific tickets
- Ticket aggregations or counts

### retrieve
Use for questions requiring documentation or best practices:
- How-to questions about processes or procedures
- Troubleshooting guides and best practices
- Policy or compliance questions
- General knowledge not in ticket data
When calling retrieve, use the 'text' parameter with your query.

## Decision Guidelines:
1. **Ticket-specific queries** → use query_tickets
2. **Knowledge/how-to queries** → use retrieve
3. **Hybrid queries** → use both tools (e.g., "What's wrong with TKT-101 and how do I fix it?")

Be concise and actionable. Reference specific ticket IDs when relevant.
"""


class ChatAgent:
    """Agent for handling ASK mode chat interactions."""

    def __init__(self):
        model_id = os.getenv("BEDROCK_MODEL_CHAT", "amazon.nova-lite-v1:0")
        print(f"[DEBUG] ChatAgent initializing with model: {model_id}")
        self.agent = Agent(
            model=model_id,
            system_prompt=SYSTEM_INSTRUCTION_CHAT
        )
        self.model = model_id

        # Knowledge Base configuration (stored for reference)
        self.kb_id = settings.knowledge_base_id
        self.kb_region = settings.knowledge_base_region
        self.kb_min_score = settings.knowledge_base_min_score
        self.kb_max_results = settings.knowledge_base_max_results

    @tool
    def query_tickets(self, ticket_ids: List[str], context_data: dict) -> List[dict]:
        """Find specific tickets by ID from the context data."""
        tickets = context_data.get('data', [])
        return [t for t in tickets if t.get('id') in ticket_ids]

    async def chat(self, message: str, history: List[dict], context: dict) -> str:
        """
        Process chat message with conversation history and context.

        Args:
            message: User's message
            history: Conversation history
            context: Context including data and briefing

        Returns:
            Agent's response string
        """

        # Add tools with context (both ticket queries and knowledge base)
        agent_with_tools = Agent(
            model=self.model,
            system_prompt=SYSTEM_INSTRUCTION_CHAT,
            tools=[self.query_tickets, retrieve]
        )

        # Build conversation context
        data_context = json.dumps(context.get('data', []), indent=2)
        briefing_context = json.dumps(context.get('briefing', {}), indent=2)

        # Format conversation history
        conversation = "\n".join([
            f"{'User' if msg['role'] == 'user' else 'Agent'}: {msg['content']}"
            for msg in history
        ])

        full_prompt = f"""CURRENT DATASET:
{data_context}

LATEST BRIEFING:
{briefing_context}

CONVERSATION HISTORY:
{conversation}

USER: {message}

AGENT:"""

        try:
            response = agent_with_tools(full_prompt)
            return str(response)
        except Exception as e:
            print(f"Chat agent error: {e}")
            return "I am having trouble connecting to the X360 core. Please check your connection."


# Initialize agent instance
chat_agent = ChatAgent()
