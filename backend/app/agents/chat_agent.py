"""
Chat Agent - Handles ASK mode interactions.
"""

from strands import Agent
from strands.tools import tool
from strands_tools import retrieve, current_time
from typing import List, Dict
import os
import json

from app.config import settings

# Set environment variables for the retrieve tool before it's used
os.environ.setdefault("KNOWLEDGE_BASE_ID", settings.knowledge_base_id)
os.environ.setdefault("AWS_REGION", settings.knowledge_base_region)
os.environ.setdefault("MIN_SCORE", str(settings.knowledge_base_min_score))
os.environ.setdefault("RETRIEVE_ENABLE_METADATA_DEFAULT", "true")

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

### current_time
Use to get the current date and time when needed for:
- Determining if tickets are overdue
- Calculating time-based SLA breaches
- Any date/time comparisons

## Decision Guidelines:
1. **Ticket-specific queries** → use query_tickets
2. **Knowledge/how-to queries** → use retrieve
3. **Hybrid queries** → use both tools (e.g., "What's wrong with TKT-101 and how do I fix it?")

## Line of Business Clarification:
Policies and procedures differ between lines of business:
- **MPS** (Managed Print Services) - printer and print-related services
- **MDS** (Managed Device Services) - device and hardware-related services
- **MCS** (Managed Collaboration Services) - collaboration and communication services

When a user asks about policies, procedures, SLAs, or compliance and it is NOT clear which line of business they are referring to, ask a clarifying question before providing an answer. For example:
- "Are you asking about MPS (Managed Print Services), MDS (Managed Device Services), or MCS (Managed Collaboration Services)?"

If the context (e.g., ticket data, previous conversation) makes the line of business clear, proceed without asking.

Be concise and actionable. Reference specific ticket IDs when relevant.
"""


def extract_citations_from_text(response_text: str) -> List[Dict]:
    """Extract citation metadata from retrieve tool output."""
    citations = []
    lines = response_text.split('\n')

    current_citation = {}
    for line in lines:
        if line.startswith('Score: '):
            if current_citation:
                citations.append(current_citation)
            current_citation = {'score': float(line.split(': ')[1])}
        elif line.startswith('Document ID: '):
            current_citation['documentId'] = line.split(': ', 1)[1]
        elif line.startswith('Metadata: ') and 'x-amz-bedrock-kb-source-uri' in line:
            import ast
            try:
                metadata_str = line.split(': ', 1)[1]
                metadata = ast.literal_eval(metadata_str)
                current_citation['sourceUri'] = metadata.get('x-amz-bedrock-kb-source-uri', '')
                current_citation['chunkId'] = metadata.get('x-amz-bedrock-kb-chunk-id', '')
                current_citation['dataSourceId'] = metadata.get('x-amz-bedrock-kb-data-source-id', '')
            except:
                pass

    if current_citation:
        citations.append(current_citation)

    return citations if citations else None


class ChatAgent:
    """Agent for handling ASK mode chat interactions."""

    def __init__(self):
        model_id = os.getenv("BEDROCK_MODEL_CHAT", "amazon.nova-lite-v1:0")
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

    async def chat(self, message: str, history: List[dict], context: dict) -> Dict:
        """
        Process chat message with conversation history and context.

        Args:
            message: User's message
            history: Conversation history
            context: Context including data and briefing

        Returns:
            Dict with 'response' (str) and 'citations' (List[dict] or None)
        """

        # Add tools with context (both ticket queries and knowledge base)
        agent_with_tools = Agent(
            model=self.model,
            system_prompt=SYSTEM_INSTRUCTION_CHAT,
            tools=[self.query_tickets, retrieve, current_time]
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

        def search_for_retrieve_in_trace(trace_dict, depth=0):
            """Recursively search for retrieve tool in trace tree."""
            trace_name = trace_dict.get('name', 'unknown')

            # Check if this is the retrieve tool (name could be 'retrieve' or 'Tool: retrieve')
            if trace_name == 'retrieve' or 'retrieve' in trace_name.lower():
                # Look for the tool output in the message
                if 'message' in trace_dict:
                    message = trace_dict['message']

                    if isinstance(message, dict) and 'content' in message:
                        tool_output = message['content']

                        # The retrieve tool returns: [{'text': 'formatted citation text'}]
                        if isinstance(tool_output, list) and len(tool_output) > 0:
                            content_block = tool_output[0]
                            if isinstance(content_block, dict) and 'text' in content_block:
                                citation_text = content_block['text']
                                return extract_citations_from_text(citation_text)

                        # Fallback: if tool_output is a string
                        elif isinstance(tool_output, str):
                            return extract_citations_from_text(tool_output)

            # Recursively search children
            if 'children' in trace_dict and trace_dict['children']:
                for child_trace in trace_dict['children']:
                    result = search_for_retrieve_in_trace(child_trace, depth + 1)
                    if result:
                        return result

            return None

        try:
            response = agent_with_tools(full_prompt)
            response_text = str(response)

            # Extract just the <response> content if present, otherwise use full text
            import re
            response_match = re.search(r'<response>(.*?)</response>', response_text, re.DOTALL)
            if response_match:
                response_text = response_match.group(1).strip()

            # Extract citations from AgentResult traces
            citations = None
            if hasattr(response, 'metrics') and hasattr(response.metrics, 'traces'):
                for trace in response.metrics.traces:
                    trace_dict = trace.to_dict() if hasattr(trace, 'to_dict') else trace.__dict__
                    citations = search_for_retrieve_in_trace(trace_dict)
                    if citations:
                        break

            print(f"[CITATIONS DEBUG] Extracted citations: {citations}")

            return {
                "response": response_text,
                "citations": citations
            }
        except Exception as e:
            print(f"Chat agent error: {e}")
            return {
                "response": "I am having trouble connecting to the X360 core. Please check your connection.",
                "citations": None
            }


# Initialize agent instance
chat_agent = ChatAgent()
