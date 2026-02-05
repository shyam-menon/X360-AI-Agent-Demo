"""
Action Agent - Handles DO mode command execution.
"""

from strands import Agent
from strands.tools import tool
from typing import List, Dict
import os
import json

SYSTEM_INSTRUCTION_ACTIONS = """
You are an AI action agent for X360. You execute operational tasks with precision.

Capabilities:
- Update ticket status
- Trigger automations
- Send notifications
- Create new tickets
- Resolve data conflicts

Always confirm what action you're taking before executing.
Provide clear feedback on action results.
"""


class ActionAgent:
    """Agent for handling DO mode action execution."""

    def __init__(self):
        model_id = os.getenv("BEDROCK_MODEL_ACTION", "amazon.nova-pro-v1:0")
        print(f"[DEBUG] ActionAgent initializing with model: {model_id}")
        self.agent = Agent(
            model=model_id,
            system_prompt=SYSTEM_INSTRUCTION_ACTIONS
        )
        self.model = model_id

    @tool
    def update_ticket_status(self, ticket_id: str, new_status: str, reason: str) -> dict:
        """Update the status of a ticket."""
        # In production, this would call the actual API
        print(f"[ACTION] Updating ticket {ticket_id} to {new_status}: {reason}")
        return {
            "success": True,
            "ticket_id": ticket_id,
            "new_status": new_status,
            "message": f"Ticket {ticket_id} updated to {new_status}"
        }

    @tool
    def trigger_automation(self, automation_name: str, parameters: dict) -> dict:
        """Trigger a predefined automation."""
        print(f"[ACTION] Triggering automation: {automation_name} with {parameters}")
        return {
            "success": True,
            "automation": automation_name,
            "message": f"Automation {automation_name} triggered successfully"
        }

    @tool
    def send_notification(self, recipient: str, message: str, priority: str = "normal") -> dict:
        """Send a notification to a team member."""
        print(f"[ACTION] Sending {priority} notification to {recipient}: {message}")
        return {
            "success": True,
            "recipient": recipient,
            "message": "Notification sent"
        }

    async def execute(self, command: str, context: dict) -> str:
        """
        Execute an action command.

        Args:
            command: User's action command
            context: Context including data

        Returns:
            Execution result message
        """

        # Create agent with action tools
        agent_with_tools = Agent(
            model=self.model,
            system_prompt=SYSTEM_INSTRUCTION_ACTIONS,
            tools=[
                self.update_ticket_status,
                self.trigger_automation,
                self.send_notification
            ]
        )

        # Provide context
        data_context = json.dumps(context.get('data', []), indent=2)

        full_prompt = f"""SYSTEM DATA:
{data_context}

USER COMMAND: {command}

Execute the requested action and provide clear feedback."""

        try:
            response = agent_with_tools(full_prompt)
            response_text = str(response)

            # Extract just the <response> content if present, otherwise use full text
            import re
            response_match = re.search(r'<response>(.*?)</response>', response_text, re.DOTALL)
            if response_match:
                response_text = response_match.group(1).strip()

            return response_text
        except Exception as e:
            print(f"Action agent error: {e}")
            return f"Failed to execute action: {str(e)}"


# Initialize agent instance
action_agent = ActionAgent()
