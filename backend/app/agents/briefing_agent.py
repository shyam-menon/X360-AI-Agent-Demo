"""
Briefing Agent (Night Watchman) - Analyzes virtualization layer data.
"""

from strands import Agent
from strands_tools import current_time
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

## Available Tools:

### current_time
Use to get the current date and time when needed for:
- Determining if tickets are overdue (past their dueDate)
- Identifying tickets approaching SLA breach (near their dueDate)
- Any date/time comparisons with ticket dates

The tool returns current time in ISO 8601 format. Compare date portions with ticket dueDate fields.

Return structured JSON with:
- summary: Brief overview of system health
- items: Array of issues with severity, type, and suggested actions
"""


class BriefingAgent:
    """Agent for analyzing data and generating morning briefings."""

    def __init__(self):
        model_id = os.getenv("BEDROCK_MODEL_BRIEFING", "amazon.nova-pro-v1:0")
        print(f"[DEBUG] BriefingAgent initializing with model: {model_id}")
        self.agent = Agent(
            model=model_id,
            system_prompt=SYSTEM_INSTRUCTION_NIGHT_WATCHMAN,
            tools=[current_time]
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
1. SLA breaches (tickets near or past due date - use the current_time tool to get today's date, then compare with each ticket's dueDate field)
2. Data conflicts (duplicate tickets with same ID but different statuses or priorities)
3. Important insights (patterns, urgent items)

IMPORTANT: Return ONLY valid JSON matching this exact structure (no markdown, no code blocks, just raw JSON):
{{
  "summary": "Brief overview of system health",
  "items": [
    {{
      "id": "unique_id",
      "type": "SLA_BREACH or DATA_CONFLICT or INSIGHT",
      "title": "Short title",
      "description": "Detailed description",
      "severity": "CRITICAL or HIGH or MEDIUM or LOW",
      "relatedTicketIds": ["ticket_id_1", "ticket_id_2"],
      "suggestedAction": "What to do about it"
    }}
  ]
}}

Return only the JSON object, nothing else.
"""

        # Call agent and parse JSON response
        try:
            response = self.agent(prompt)
            response_text = str(response)

            # Try to parse JSON from response
            # Remove markdown code blocks if present
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            elif "```" in response_text:
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()

            # Parse JSON
            result = json.loads(response_text)

            # Validate structure
            if 'summary' not in result or 'items' not in result:
                raise ValueError("Response missing required fields")

            return result

        except Exception as e:
            print(f"Briefing agent error: {e}")
            return {
                "summary": "System is offline. Displaying cached operational data.",
                "items": []
            }


# Initialize agent instance
briefing_agent = BriefingAgent()
