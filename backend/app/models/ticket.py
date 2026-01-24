"""
Ticket model matching the TypeScript Ticket interface.
"""

from pydantic import BaseModel
from typing import Literal


class Ticket(BaseModel):
    """Ticket from virtualization layer (ServiceNow, Salesforce, Jira, etc.)"""

    id: str
    customer: str
    title: str
    status: str
    priority: Literal["Low", "Medium", "High", "Critical"]
    createdDate: str
    dueDate: str
    source: Literal["ServiceNow", "Salesforce", "Jira", "Zendesk", "Datadog", "PagerDuty"]
    assignee: str
