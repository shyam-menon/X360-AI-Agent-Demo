"""
Briefing Agent (Night Watchman) - Analyzes virtualization layer data.
"""

from strands import Agent
from typing import List, Dict
import os
import json

# System instruction from constants.ts
SYSTEM_INSTRUCTION_NIGHT_WATCHMAN = """
You are "Night Watchman," an AI agent that monitors a unified virtualization layer
aggregating data from ServiceNow, Salesforce, Jira, Zendesk, Datadog, and PagerDuty.

Your purpose:
- Detect SLA breaches (tickets approaching or past due dates)
- Identify data conflicts between systems (duplicates, inconsistencies)
- Surface actionable insights (patterns, urgent items, resource bottlenecks)

Return structured JSON with:
- summary: Brief overview of system health
- items: Array of issues with severity, type, and suggested actions
"""


class BriefingAgent:
    """Agent for analyzing data and generating morning briefings."""

    def __init__(self):
        self.agent = Agent(
            model=os.getenv("BEDROCK_MODEL_BRIEFING", "us.anthropic.claude-sonnet-4-20250514"),
            system_prompt=SYSTEM_INSTRUCTION_NIGHT_WATCHMAN
        )

    async def analyze_data(self, data: List[dict]) -> dict:
        """
        Analyze virtualization layer data and generate briefing.

        Args:
            data: List of tickets from various systems

        Returns:
            Dictionary with summary and list of briefing items
        """
        from pydantic import BaseModel

        # Define the expected output structure
        class BriefingOutput(BaseModel):
            summary: str
            items: List[dict]

        # Format data for analysis
        data_context = json.dumps(data, indent=2)

        prompt = f"""Analyze this data from the virtualization layer and generate a morning briefing.

DATA:
{data_context}

Identify:
1. SLA breaches (tickets near or past due date)
2. Data conflicts (duplicate tickets, inconsistent statuses)
3. Important insights (patterns, urgent items)

Return JSON matching this structure:
{{
  "summary": "Brief overview of system health",
  "items": [
    {{
      "id": "unique_id",
      "type": "SLA_BREACH | DATA_CONFLICT | INSIGHT",
      "title": "Short title",
      "description": "Detailed description",
      "severity": "CRITICAL | HIGH | MEDIUM | LOW",
      "relatedTicketIds": ["ticket_id_1", "ticket_id_2"],
      "suggestedAction": "What to do about it"
    }}
  ]
}}
"""

        # Use extract() for structured output
        try:
            result = self.agent.extract(BriefingOutput, prompt)
            return result.model_dump()
        except Exception as e:
            print(f"Briefing agent error: {e}")
            return {
                "summary": "System is offline. Displaying cached operational data.",
                "items": []
            }


# Initialize agent instance
briefing_agent = BriefingAgent()
