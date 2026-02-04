export enum TicketStatus {
    Open = "Open",
    Pending = "Pending",
    Closed = "Closed",
    Resolved = "Resolved",
    Investigating = "Investigating"
  }
  
  export interface Ticket {
    id: string;
    customer: string;
    title: string;
    status: TicketStatus | string;
    priority: "Low" | "Medium" | "High" | "Critical";
    createdDate: string; // ISO Date
    dueDate: string; // ISO Date
    source: "ServiceNow" | "Salesforce" | "Jira" | "Zendesk" | "Datadog" | "PagerDuty";
    assignee: string;
  }
  
  export interface BriefingItem {
    id: string;
    type: "SLA_BREACH" | "DATA_CONFLICT" | "INSIGHT";
    title: string;
    description: string;
    severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
    relatedTicketIds: string[];
    suggestedAction?: string;
  }
  
  export interface BriefingResponse {
    summary: string;
    items: BriefingItem[];
  }

  export interface Citation {
    score: number;
    documentId: string;
    sourceUri?: string;
    chunkId?: string;
    dataSourceId?: string;
  }

  export interface ChatMessage {
    role: "user" | "model";
    content: string;
    timestamp: number;
    isAction?: boolean; // If true, renders a special UI for "Do" actions
    citations?: Citation[];
  }

  export type ViewMode = "TELL" | "ASK" | "DO" | "DATA";