# X360 AI Agent

An AI-powered operational assistant that monitors and manages tickets across multiple systems (ServiceNow, Salesforce, Jira, Zendesk, Datadog, PagerDuty) using AWS Bedrock and Strands Agents.

## Architecture

```
┌─────────────────────┐      ┌──────────────────────┐      ┌─────────────────┐
│  React Frontend     │ HTTP │  FastAPI Backend     │ SDK  │  AWS Bedrock    │
│  (Vite + TypeScript)├─────►│  (Python + Strands)  ├─────►│  (Nova Models)  │
│  Port 3000          │◄─────┤  Port 8000           │◄─────┤                 │
└─────────────────────┘      └──────────────────────┘      └─────────────────┘
```

## Features

- **TELL Mode (Dashboard)** - Morning briefing with SLA breaches, data conflicts, and insights
- **ASK Mode (Agent)** - Natural language Q&A about tickets and system data
- **DO Mode (Actions)** - Execute operational commands and automations
- **DATA Mode (Viewer)** - View raw virtualization layer data

---

## Prerequisites

- **Node.js** v18+ (for frontend)
- **Python** 3.10+ (for backend)
- **AWS Account** with Bedrock access enabled
- **AWS CLI** configured with credentials (`aws configure`)

### AWS Bedrock Model Access

Before running the application, ensure you have access to the following models in AWS Bedrock:

1. Go to [AWS Bedrock Console](https://console.aws.amazon.com/bedrock)
2. Navigate to **Model access**
3. Request access to:
   - Amazon Nova Lite
   - Amazon Nova Pro

---

## Quick Start

### 1. Clone and Install Dependencies

```bash
# Clone the repository
git clone <repository-url>
cd X360Agent

# Install frontend dependencies
npm install

# Setup backend
cd backend
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

#### Backend Configuration

Create or edit `backend/.env`:

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

# CORS - Add your frontend URLs (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

#### Frontend Configuration

Create or edit `.env.local` in the root directory:

```env
# Backend API URL
VITE_API_BASE_URL=http://localhost:8000
```

### 3. Start the Application

You need two terminals - one for the backend and one for the frontend.

#### Terminal 1: Start Backend

```bash
cd backend

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

#### Terminal 2: Start Frontend

```bash
# From the root X360Agent directory
npm run dev
```

You should see:
```
VITE v6.x.x  ready in xxx ms

➜  Local:   http://localhost:3000/
➜  Network: http://192.168.x.x:3000/
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

---

## Testing the Application Modes

The application has 4 modes accessible via the bottom navigation bar. Here's how to test each one:

### TELL Mode (Dashboard) - Morning Briefing

**What it does:** Analyzes ticket data and generates a morning briefing with SLA breaches, data conflicts, and insights.

**How to test:**

1. Open http://localhost:3000
2. The app starts in TELL mode (Dashboard tab is active)
3. Wait 2-9 seconds for the briefing to load from the backend
4. You should see:
   - A summary card at the top with system health overview
   - Cards showing SLA breaches (overdue tickets)
   - Cards showing data conflicts (same ticket ID with different statuses)
   - Severity indicators (CRITICAL, HIGH, MEDIUM, LOW)
   - Suggested actions for each issue

**Expected results:**
- TKT-99 flagged as SLA breach (overdue)
- TKT-101 flagged as data conflict (Salesforce vs ServiceNow status mismatch)
- TKT-108 flagged as data conflict (Datadog vs PagerDuty status/priority mismatch)

**If it fails:** You'll see "System is offline. Displaying cached operational data." - check backend logs.

---

### ASK Mode (Agent) - Q&A Chat

**What it does:** Natural language Q&A about tickets, data, and system insights.

**How to test:**

1. Click the **Agent** tab in the bottom navigation
2. Type a question in the chat input and press Enter
3. Wait 2-4 seconds for the AI response

**Sample questions to try:**

| Question | Expected Response |
|----------|-------------------|
| "What tickets are overdue?" | Lists TKT-99 and TKT-112 with details |
| "Tell me about TKT-101" | Explains the data conflict between systems |
| "Which tickets are Critical priority?" | Lists TKT-99 and TKT-108 |
| "What should I prioritize today?" | Recommends focusing on SLA breaches first |
| "Summarize the data conflicts" | Explains TKT-101 and TKT-108 conflicts |
| "Who is assigned to the server outage?" | Shows TKT-99 is unassigned |

**Multi-turn conversation test:**
1. Ask: "What tickets are from Acme Corp?"
2. Follow up: "What's the status of that ticket?"
3. The agent should remember context from the previous question

---

### DO Mode (Actions) - Command Execution

**What it does:** Executes operational commands like updating tickets, sending notifications, and triggering automations.

**How to test:**

1. Click the **Actions** tab in the bottom navigation
2. You'll see suggested actions based on briefing issues
3. Type a command in the chat input and press Enter
4. Wait 3-8 seconds for execution feedback

**Sample commands to try:**

| Command | Expected Response |
|---------|-------------------|
| "Update TKT-99 status to In Progress" | Confirms ticket status update |
| "Assign TKT-99 to DevOps team" | Confirms assignment change |
| "Send notification to Sarah about TKT-101 conflict" | Confirms notification sent |
| "Escalate TKT-99 to management" | Confirms escalation action |
| "Trigger the SLA breach playbook for TKT-99" | Confirms automation triggered |
| "Resolve the data conflict for TKT-101" | Explains resolution steps and confirms action |

**Quick action test:**
1. In TELL mode, click on a briefing item (e.g., an SLA breach card)
2. This switches to ASK mode with context
3. Ask "Run the fix playbook"
4. The agent will switch to DO mode and execute

---

### DATA Mode (Raw Data) - Data Viewer

**What it does:** Displays the raw ticket data from the virtualization layer.

**How to test:**

1. Click the **Raw Data** tab in the bottom navigation
2. You should see a table/list of all tickets
3. Verify you can see:
   - 7 tickets total (including duplicates for conflicts)
   - Tickets from different sources (Jira, ServiceNow, Salesforce, etc.)
   - Different priorities and statuses

**Data verification:**

| Ticket ID | Customer | Source | Status | Notes |
|-----------|----------|--------|--------|-------|
| TKT-99 | Acme Corp | Jira | Open | SLA breach - overdue |
| TKT-101 | Globex Inc | Salesforce | Closed | Conflict - Version A |
| TKT-101 | Globex Inc | ServiceNow | Pending Vendor | Conflict - Version B |
| TKT-105 | Soylent Corp | Zendesk | Open | Normal ticket |
| TKT-108 | Massive Dynamic | Datadog | Resolved | Conflict - Version A |
| TKT-108 | Massive Dynamic | PagerDuty | Open | Conflict - Version B |
| TKT-112 | Initech | ServiceNow | Open | Due today |

---

### End-to-End Test Flow

To verify the complete system is working:

1. **Start fresh** - Open http://localhost:3000
2. **TELL mode** - Wait for briefing, verify SLA breaches and conflicts appear
3. **Click a briefing item** - Should switch to ASK mode with context
4. **Ask a question** - "What's the recommended fix?"
5. **Switch to DO mode** - Click Actions tab
6. **Execute a command** - "Update the ticket status to In Progress"
7. **Verify response** - Should confirm action taken
8. **Check DATA mode** - Verify raw data is visible

**Success criteria:**
- All 4 modes load without errors
- Briefing shows SLA breaches and conflicts
- Chat responds to questions with relevant answers
- Actions execute and return confirmation
- Raw data displays all tickets

---

### Testing via API (Backend Only)

You can also test the backend directly without the frontend:

**Test TELL (Briefing):**
```bash
curl -X POST http://localhost:8000/api/v1/briefing \
  -H "Content-Type: application/json" \
  -d '{"data": [{"id": "TKT-99", "customer": "Acme Corp", "title": "Server Outage", "status": "Open", "priority": "Critical", "createdDate": "2026-01-01", "dueDate": "2026-01-20", "source": "Jira", "assignee": "Unassigned"}]}'
```

**Test ASK:**
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What tickets are overdue?", "history": [], "mode": "ASK", "context": {"data": [{"id": "TKT-99", "customer": "Acme", "title": "Outage", "status": "Open", "priority": "Critical", "createdDate": "2026-01-01", "dueDate": "2026-01-20", "source": "Jira", "assignee": "Unassigned"}]}}'
```

**Test DO:**
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Update TKT-99 to In Progress", "history": [], "mode": "DO", "context": {"data": [{"id": "TKT-99", "customer": "Acme", "title": "Outage", "status": "Open", "priority": "Critical", "createdDate": "2026-01-01", "dueDate": "2026-01-20", "source": "Jira", "assignee": "Unassigned"}]}}'
```

---

## Project Structure

```
X360Agent/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── main.py            # FastAPI application entry point
│   │   ├── config.py          # Configuration and settings
│   │   ├── agents/            # Strands AI agents
│   │   │   ├── briefing_agent.py   # Morning briefing agent
│   │   │   ├── chat_agent.py       # ASK mode agent
│   │   │   └── action_agent.py     # DO mode agent
│   │   ├── models/            # Pydantic models
│   │   │   ├── briefing.py
│   │   │   ├── chat.py
│   │   │   └── ticket.py
│   │   └── routers/           # API endpoints
│   │       ├── briefing.py
│   │       └── chat.py
│   ├── tests/                 # Test suite
│   ├── test_data/             # Test scenarios
│   ├── .env                   # Backend environment config
│   ├── requirements.txt       # Python dependencies
│   └── API_DOCUMENTATION.md   # API reference
│
├── components/                # React components
│   ├── ChatInterface.tsx
│   ├── Dashboard.tsx
│   ├── DataViewer.tsx
│   └── Icons.tsx
├── services/
│   └── backendService.ts      # Backend API client
├── App.tsx                    # Main React application
├── constants.ts               # System constants and mock data
├── types.ts                   # TypeScript interfaces
├── index.tsx                  # React entry point
├── vite.config.ts             # Vite configuration
├── .env.local                 # Frontend environment config
├── package.json               # Node.js dependencies
└── README.md                  # This file
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint - API info |
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/briefing` | Generate morning briefing |
| POST | `/api/v1/chat` | Chat (ASK/DO modes) |

### Example: Health Check

```bash
curl http://localhost:8000/api/v1/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "bedrock_region": "us-east-1"
}
```

### Example: Morning Briefing

```bash
curl -X POST http://localhost:8000/api/v1/briefing \
  -H "Content-Type: application/json" \
  -d '{"data": [{"id": "TKT-99", "customer": "Acme", "title": "Outage", "status": "Open", "priority": "Critical", "createdDate": "2026-01-01", "dueDate": "2026-01-20", "source": "Jira", "assignee": "Unassigned"}]}'
```

### Example: Chat (ASK Mode)

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What tickets are overdue?", "history": [], "mode": "ASK", "context": {"data": [...]}}'
```

See [backend/API_DOCUMENTATION.md](backend/API_DOCUMENTATION.md) for complete API reference.

---

## Running Tests

### Backend Tests

```bash
cd backend

# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Run all tests
python -m pytest tests/ -v

# Run specific test file
python tests/test_api_endpoints.py
python tests/test_briefing_agent.py
python tests/test_chat_agent.py
python tests/test_action_agent.py
```

### Test Results

| Component | Tests | Pass Rate |
|-----------|-------|-----------|
| Briefing Agent | 5 | 80% |
| Chat Agent | 18 | 100% |
| Action Agent | 16 | 93.8% |
| API Endpoints | 6 | 100% |
| **Total** | **46** | **95.7%** |

---

## Troubleshooting

### CORS Errors

If you see CORS errors in the browser console:

1. Check that the backend is running
2. Verify your frontend URL is in `backend/.env` under `CORS_ORIGINS`
3. Restart the backend after modifying `.env`

Example - add your network IP:
```env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://192.168.1.100:3000
```

### AWS Credentials Not Found

```
NoCredentialsError: Unable to locate credentials
```

**Solution:**
```bash
# Configure AWS CLI
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
```

### Bedrock Model Access Denied

```
AccessDeniedException: You don't have access to the model
```

**Solution:**
1. Go to AWS Bedrock Console
2. Navigate to **Model access**
3. Request access to Nova Lite and Nova Pro models
4. Wait for approval (usually instant)

### Backend Not Starting

Check if port 8000 is already in use:

```bash
# Windows
netstat -ano | findstr :8000

# macOS/Linux
lsof -i :8000
```

### Frontend Not Connecting to Backend

1. Verify backend is running: `curl http://localhost:8000/api/v1/health`
2. Check `.env.local` has correct `VITE_API_BASE_URL`
3. Restart the frontend after changing `.env.local`

---

## Development

### Adding a New Agent

1. Create agent file in `backend/app/agents/`
2. Add Pydantic models in `backend/app/models/`
3. Create router in `backend/app/routers/`
4. Register router in `backend/app/main.py`
5. Add frontend API call in `services/backendService.ts`

### Modifying System Prompts

Agent system prompts are defined in:
- `backend/app/agents/briefing_agent.py` - Night Watchman prompt
- `backend/app/agents/chat_agent.py` - ASK mode prompt
- `backend/app/agents/action_agent.py` - DO mode prompt

---

## Performance

| Operation | Model | Avg Response Time |
|-----------|-------|-------------------|
| Briefing | Nova Pro | 2-9 seconds |
| Chat (ASK) | Nova Lite | 2-4 seconds |
| Chat (DO) | Nova Pro | 3-8 seconds |

---

## Cost Estimation

### AWS Bedrock Pricing (us-east-1)

| Model | Input | Output |
|-------|-------|--------|
| Nova Lite | $0.06/1M tokens | $0.24/1M tokens |
| Nova Pro | $0.80/1M tokens | $3.20/1M tokens |

### Estimated Monthly Cost (1000 users/day)

- Morning briefings: ~$30/month
- Chat interactions: ~$15/month
- Actions: ~$20/month
- **Total: ~$65/month**

---

## Documentation

| Document | Description |
|----------|-------------|
| [CLAUDE.md](CLAUDE.md) | Full migration guide and architecture |
| [CURRENT_STATUS.md](CURRENT_STATUS.md) | Project status and progress |
| [backend/API_DOCUMENTATION.md](backend/API_DOCUMENTATION.md) | Complete API reference |
| [backend/tests/TEST_RESULTS_SUMMARY.md](backend/tests/TEST_RESULTS_SUMMARY.md) | Test results |

---

## License

Proprietary - Internal Use Only
