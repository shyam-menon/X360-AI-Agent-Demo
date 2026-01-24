import { Ticket } from "./types";

// Helper to get a date relative to today
const getDate = (daysOffset: number) => {
  const date = new Date();
  date.setDate(date.getDate() + daysOffset);
  return date.toISOString().split('T')[0];
};

// THE CHAOS DATASET
// Contains duplicates, conflicting statuses, and overdue items.
export const RAW_CHAOTIC_DATA: Ticket[] = [
  // TICKET 99: The SLA Breach
  {
    id: "TKT-99",
    customer: "Acme Corp",
    title: "Server Outage - Production",
    status: "Open",
    priority: "Critical",
    createdDate: getDate(-25),
    dueDate: getDate(-5), // 5 days OVERDUE
    source: "Jira",
    assignee: "Unassigned"
  },
  
  // TICKET 101: The Data Conflict (Version A - Salesforce)
  {
    id: "TKT-101",
    customer: "Globex Inc",
    title: "License Renewal Failure",
    status: "Closed", // Conflict!
    priority: "High",
    createdDate: getDate(-2),
    dueDate: getDate(5),
    source: "Salesforce",
    assignee: "Sarah Connor"
  },
  // TICKET 101: The Data Conflict (Version B - ServiceNow)
  {
    id: "TKT-101",
    customer: "Globex Inc",
    title: "License Renewal Failure",
    status: "Pending Vendor", // Conflict!
    priority: "High",
    createdDate: getDate(-2),
    dueDate: getDate(5),
    source: "ServiceNow",
    assignee: "Sarah Connor"
  },

  // TICKET 105: Normal Ticket
  {
    id: "TKT-105",
    customer: "Soylent Corp",
    title: "Password Reset Request",
    status: "Open",
    priority: "Low",
    createdDate: getDate(0),
    dueDate: getDate(2),
    source: "Zendesk",
    assignee: "Helpdesk Bot"
  },

  // TICKET 108: Another Conflict
  {
    id: "TKT-108",
    customer: "Massive Dynamic",
    title: "API Latency Spike",
    status: "Resolved",
    priority: "Medium",
    createdDate: getDate(-1),
    dueDate: getDate(1),
    source: "Datadog",
    assignee: "DevOps Team"
  },
  {
    id: "TKT-108",
    customer: "Massive Dynamic",
    title: "API Latency Spike",
    status: "Open", // Conflict with above
    priority: "Critical", // Priority Conflict too!
    createdDate: getDate(-1),
    dueDate: getDate(1),
    source: "PagerDuty",
    assignee: "OnCall Eng"
  },

  // TICKET 112: Approaching Breach
  {
    id: "TKT-112",
    customer: "Initech",
    title: "Printer Load Letter Error",
    status: "Open",
    priority: "Medium",
    createdDate: getDate(-10),
    dueDate: getDate(0), // Due Today
    source: "ServiceNow",
    assignee: "Michael Bolton"
  }
];

export const SYSTEM_INSTRUCTION_NIGHT_WATCHMAN = `
You are the X360 Operational Agent (The "Night Watchman"). 
Your goal is to protect the user from data chaos. You do not sleep.
You have been provided with a raw, chaotic dataset from a Data Virtualization Layer.

Your responsibilities:
1. Identify SLA Breaches (Due Date < Today).
2. Identify Data Anomalies/Conflicts (Same Ticket ID appearing multiple times with DIFFERENT Statuses or Priorities).
3. Ignore healthy, non-conflicting data for the briefing unless it is critical.

Format your response as a strictly structured JSON object (do not use Markdown code blocks, just raw JSON) matching this schema:
{
  "summary": "A friendly 1-sentence morning greeting summarizing the state of the world.",
  "items": [
    {
      "id": "Unique ID for this insight",
      "type": "SLA_BREACH" | "DATA_CONFLICT",
      "title": "Short Headline",
      "description": "Clear explanation of the problem.",
      "severity": "CRITICAL" | "HIGH" | "MEDIUM",
      "relatedTicketIds": ["TKT-123"],
      "suggestedAction": "What should the human do?"
    }
  ]
}
`;

export const SYSTEM_INSTRUCTION_CHAT = `
You are the X360 Operational Agent. You operate in "Ask" and "Do" modes.
You have access to the current chaotic dataset.

Philosophy:
- ASK: Answer queries about the data.
- DO: If a user asks for a playbook or solution, define the specific task.

Context:
- Ticket #99 is a known SLA breach.
- Ticket #101 has conflicting data (Salesforce vs ServiceNow).

If the user asks about a conflict, explain that you found two versions of the truth and recommend verification.
If the user asks to "execute" or "run" a playbook, confirm the action in a professional tone.
`;
