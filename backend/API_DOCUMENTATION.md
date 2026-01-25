# X360 AI Agent - API Documentation

**Version:** 1.0.0
**Base URL:** `http://localhost:8000`
**Date:** January 24, 2026

---

## Overview

The X360 AI Agent API provides RESTful endpoints for interacting with AI agents powered by AWS Bedrock and the Strands framework. The API supports three core operations:

1. **Morning Briefings** - Analyze virtualization layer data
2. **Chat (ASK Mode)** - Answer questions about tickets and system data
3. **Actions (DO Mode)** - Execute operational commands

---

## Table of Contents

1. [Authentication](#authentication)
2. [Endpoints](#endpoints)
   - [Root Endpoint](#root-endpoint)
   - [Health Check](#health-check)
   - [Briefing Analysis](#briefing-analysis)
   - [Chat (ASK/DO Modes)](#chat-askdo-modes)
3. [Data Models](#data-models)
4. [Error Handling](#error-handling)
5. [Examples](#examples)
6. [Rate Limiting](#rate-limiting)

---

## Authentication

Currently, the API does not require authentication. This will be added in future versions.

**CORS:** Configured to allow requests from:
- `http://localhost:3000` (React dev server)
- `http://localhost:5173` (Vite dev server)

---

## Endpoints

### Root Endpoint

**GET** `/`

Returns basic API information.

**Response:**
```json
{
  "message": "X360 AI Agent API",
  "status": "online"
}
```

**Status Codes:**
- `200 OK` - API is running

---

### Health Check

**GET** `/api/v1/health`

Health check endpoint for monitoring and load balancers.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "bedrock_region": "us-east-1"
}
```

**Status Codes:**
- `200 OK` - Service is healthy

---

### Briefing Analysis

**POST** `/api/v1/briefing`

Analyzes virtualization layer data and generates a morning briefing with SLA breaches, data conflicts, and insights.

**Request Body:**
```json
{
  "data": [
    {
      "id": "TKT-99",
      "customer": "Acme Corp",
      "title": "Server Outage - Production",
      "status": "Open",
      "priority": "Critical",
      "createdDate": "2025-12-30",
      "dueDate": "2026-01-19",
      "source": "Jira",
      "assignee": "Unassigned"
    }
  ]
}
```

**Response:**
```json
{
  "summary": "There are critical SLA breaches and data conflicts that require immediate attention.",
  "items": [
    {
      "id": "TKT-99",
      "type": "SLA_BREACH",
      "title": "Critical Server Outage",
      "description": "Production server outage ticket is open and approaching due date.",
      "severity": "CRITICAL",
      "relatedTicketIds": ["TKT-99"],
      "suggestedAction": "Assign a team to investigate and resolve the server outage immediately."
    }
  ]
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `data` | Array of Ticket objects | Yes | Virtualization layer data from multiple systems |

**Status Codes:**
- `200 OK` - Briefing generated successfully
- `422 Unprocessable Entity` - Invalid request format
- `500 Internal Server Error` - Agent processing failed (returns fallback response)

**Performance:**
- Average response time: 2-9 seconds
- Uses: `amazon.nova-pro-v1:0` model

---

### Chat (ASK/DO Modes)

**POST** `/api/v1/chat`

Send messages to the AI agent in either ASK mode (questions) or DO mode (actions).

**Request Body:**
```json
{
  "message": "What tickets are overdue?",
  "history": [
    {
      "role": "user",
      "content": "Previous message",
      "timestamp": 1706123456789,
      "isAction": false
    }
  ],
  "mode": "ASK",
  "context": {
    "data": [...],
    "briefing": {...}
  }
}
```

**Response:**
```json
{
  "response": "There are two overdue tickets: TKT-99 (Server Outage) and TKT-112 (Printer Error).",
  "timestamp": 1706123456789
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `message` | string | Yes | User's message or command |
| `history` | Array of ChatMessage | Yes | Conversation history (can be empty array) |
| `mode` | "ASK" \| "DO" | Yes | ASK for questions, DO for actions |
| `context` | object | No | Context including data and briefing |

**Modes:**

**ASK Mode** - For questions and analysis
- Uses: `amazon.nova-lite-v1:0` model
- Average response time: 2-4 seconds
- Capabilities:
  - Answer questions about tickets
  - Analyze patterns and trends
  - Provide recommendations
  - Explain conflicts and issues

**DO Mode** - For executing actions
- Uses: `amazon.nova-pro-v1:0` model
- Average response time: 3-8 seconds
- Capabilities:
  - Update ticket status
  - Send notifications
  - Trigger automations
  - Execute multi-step workflows

**Status Codes:**
- `200 OK` - Message processed successfully
- `422 Unprocessable Entity` - Invalid request format
- `500 Internal Server Error` - Agent processing failed (returns fallback response)

---

## Data Models

### Ticket

```typescript
{
  id: string;              // Unique ticket ID
  customer: string;        // Customer name
  title: string;           // Ticket title
  status: string;          // Current status
  priority: "Low" | "Medium" | "High" | "Critical";
  createdDate: string;     // ISO date string
  dueDate: string;         // ISO date string
  source: "ServiceNow" | "Salesforce" | "Jira" | "Zendesk" | "Datadog" | "PagerDuty";
  assignee: string;        // Assigned user/team
}
```

### BriefingItem

```typescript
{
  id: string;              // Unique item ID
  type: "SLA_BREACH" | "DATA_CONFLICT" | "INSIGHT";
  title: string;           // Brief title
  description: string;     // Detailed description
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  relatedTicketIds: string[];  // Related ticket IDs
  suggestedAction: string | null;  // Recommended action
}
```

### ChatMessage

```typescript
{
  role: "user" | "model";  // Message sender
  content: string;         // Message text
  timestamp: number;       // Unix timestamp (ms)
  isAction: boolean;       // Optional: true for DO mode
}
```

---

## Error Handling

### Validation Errors (422)

When request validation fails:

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "data"],
      "msg": "Field required",
      "input": {...}
    }
  ]
}
```

### Agent Failures (500 → 200 with fallback)

When the agent encounters an error, a graceful fallback response is returned with status 200:

**Briefing Failure:**
```json
{
  "summary": "System is offline. Displaying cached operational data.",
  "items": []
}
```

**Chat Failure:**
```json
{
  "response": "I am having trouble connecting to the X360 core. Please check your connection.",
  "timestamp": 1706123456789
}
```

---

## Examples

### Example 1: Morning Briefing

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/briefing \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {
        "id": "TKT-99",
        "customer": "Acme Corp",
        "title": "Server Outage - Production",
        "status": "Open",
        "priority": "Critical",
        "createdDate": "2025-12-30",
        "dueDate": "2026-01-19",
        "source": "Jira",
        "assignee": "Unassigned"
      }
    ]
  }'
```

**Response:**
```json
{
  "summary": "There is 1 critical SLA breach requiring immediate attention.",
  "items": [
    {
      "id": "TKT-99",
      "type": "SLA_BREACH",
      "title": "Critical Server Outage",
      "description": "Production server outage ticket is open and approaching due date.",
      "severity": "CRITICAL",
      "relatedTicketIds": ["TKT-99"],
      "suggestedAction": "Assign a team to investigate and resolve the server outage immediately."
    }
  ]
}
```

---

### Example 2: ASK Mode - Questions

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What tickets are overdue?",
    "history": [],
    "mode": "ASK",
    "context": {
      "data": [...]
    }
  }'
```

**Response:**
```json
{
  "response": "There are two overdue tickets:\n\n1. TKT-99 - Server Outage (Due: 2026-01-19)\n2. TKT-112 - Printer Error (Due: 2026-01-24)\n\nBoth require immediate attention.",
  "timestamp": 1706123456789
}
```

---

### Example 3: DO Mode - Actions

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Update TKT-99 status to In Progress and notify DevOps team",
    "history": [],
    "mode": "DO",
    "context": {
      "data": [...]
    }
  }'
```

**Response:**
```json
{
  "response": "I have completed the following actions:\n\n1. Updated TKT-99 status to 'In Progress'\n2. Sent notification to DevOps team about the update\n\nBoth actions completed successfully.",
  "timestamp": 1706123456789
}
```

---

### Example 4: Multi-turn Conversation

**Turn 1:**
```json
{
  "message": "What should I prioritize today?",
  "history": [],
  "mode": "ASK",
  "context": {"data": [...]}
}
```

**Response:**
```json
{
  "response": "You should prioritize these tickets:\n1. TKT-99 - Critical server outage\n2. TKT-108 - Critical API latency\n3. TKT-112 - Medium priority, due today",
  "timestamp": 1706123456789
}
```

**Turn 2:**
```json
{
  "message": "Tell me more about the first one",
  "history": [
    {
      "role": "user",
      "content": "What should I prioritize today?",
      "timestamp": 1706123456789
    },
    {
      "role": "model",
      "content": "You should prioritize these tickets...",
      "timestamp": 1706123456790
    }
  ],
  "mode": "ASK",
  "context": {"data": [...]}
}
```

**Response:**
```json
{
  "response": "TKT-99 is a critical server outage affecting Acme Corp's production environment. It's been open since 2025-12-30 and is overdue by 5 days. Currently unassigned.",
  "timestamp": 1706123456791
}
```

---

## Rate Limiting

**Current:** No rate limiting implemented

**Future:** Will implement rate limiting based on:
- IP address: 100 requests/minute
- Session ID: 50 requests/minute
- Endpoint-specific limits for expensive operations

---

## Performance

### Benchmarks

| Endpoint | Model | Avg Response Time | Max Tokens |
|----------|-------|-------------------|------------|
| `/api/v1/briefing` | Nova Pro | 2-9s | ~2000 |
| `/api/v1/chat` (ASK) | Nova Lite | 2-4s | ~1000 |
| `/api/v1/chat` (DO) | Nova Pro | 3-8s | ~1500 |

### Optimization Tips

1. **Batch Briefings** - Run once per day, cache results
2. **Context Size** - Keep data payload under 100 tickets
3. **Conversation History** - Limit to last 10 messages
4. **Streaming** - Future enhancement for real-time responses

---

## Development

### Running the Server

```bash
# Development mode with auto-reload
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Environment Variables

Create a `.env` file in the `backend` directory:

```env
# AWS Bedrock Configuration
AWS_DEFAULT_REGION=us-east-1

# Bedrock Models
BEDROCK_MODEL_BRIEFING=amazon.nova-pro-v1:0
BEDROCK_MODEL_CHAT=amazon.nova-lite-v1:0
BEDROCK_MODEL_ACTION=amazon.nova-pro-v1:0

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Testing

```bash
# Run all tests
python tests/test_briefing_agent.py
python tests/test_chat_agent.py
python tests/test_action_agent.py
python tests/test_api_endpoints.py

# Test specific endpoint
curl http://localhost:8000/api/v1/health
```

---

## Changelog

### Version 1.0.0 (2026-01-24)

**Added:**
- Initial API release
- Briefing endpoint with Nova Pro
- Chat endpoint (ASK/DO modes)
- Health check endpoint
- Comprehensive error handling
- Test suite with 100% pass rate

**Models:**
- Briefing: `amazon.nova-pro-v1:0`
- Chat (ASK): `amazon.nova-lite-v1:0`
- Action (DO): `amazon.nova-pro-v1:0`

---

## Support

**Issues:** https://github.com/yourorg/x360agent/issues
**Docs:** https://docs.x360agent.com
**API Status:** https://status.x360agent.com

---

## License

Proprietary - Internal Use Only

---

*API Documentation Generated: 2026-01-24*
*Next Update: After frontend integration*
