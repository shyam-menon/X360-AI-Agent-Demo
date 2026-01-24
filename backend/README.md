# X360 AI Agent - Backend

FastAPI backend with Strands agents framework and AWS Bedrock integration.

## Setup

### 1. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure AWS Credentials

Copy `.env.template` to `.env` and fill in your AWS credentials:

```bash
cp .env.template .env
```

Then edit `.env` with your actual AWS credentials.

### 4. Request AWS Bedrock Model Access

1. Login to AWS Console
2. Navigate to Amazon Bedrock → Model access
3. Request access to:
   - Claude Sonnet 4 (for complex analysis)
   - Amazon Nova Lite (for fast chat)
4. Wait for approval (usually instant)

### 5. Run the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check
- `GET /` - Root endpoint
- `GET /api/v1/health` - Health check

### Briefing
- `POST /api/v1/briefing` - Run morning briefing analysis

### Chat
- `POST /api/v1/chat` - Send chat message (ASK or DO mode)

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Settings and environment config
│   ├── models/              # Pydantic models
│   │   ├── briefing.py
│   │   ├── chat.py
│   │   └── ticket.py
│   ├── agents/              # Strands agents
│   │   ├── briefing_agent.py
│   │   ├── chat_agent.py
│   │   └── action_agent.py
│   ├── services/
│   │   └── bedrock_client.py
│   └── routers/
│       ├── briefing.py
│       └── chat.py
├── tests/
│   ├── test_agents.py
│   └── test_api.py
├── requirements.txt
├── .env
└── README.md
```

## Testing

```bash
# Run tests
pytest

# Test with curl
curl http://localhost:8000/api/v1/health
```
