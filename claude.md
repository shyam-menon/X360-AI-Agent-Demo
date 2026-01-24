# AWS Bedrock and Strands Agents - React Integration Guide

This document provides comprehensive context for building React applications that integrate with AWS Bedrock and Strands Agents framework. Use this as a reference when developing AI-powered features in your React application.

---

## Table of Contents

1. [Overview](#overview)
2. [AWS Bedrock Fundamentals](#aws-bedrock-fundamentals)
3. [Strands Agents Framework](#strands-agents-framework)
4. [Architecture Patterns](#architecture-patterns)
5. [Backend Integration](#backend-integration)
6. [React Frontend Implementation](#react-frontend-implementation)
7. [Authentication & Security](#authentication--security)
8. [Tools and Custom Capabilities](#tools-and-custom-capabilities)
9. [Streaming & Real-time Responses](#streaming--real-time-responses)
10. [Best Practices](#best-practices)
11. [Code Examples](#code-examples)
12. [Troubleshooting](#troubleshooting)

---

## Overview

### What is AWS Bedrock?

AWS Bedrock is a fully managed service providing access to foundation models from leading AI companies through a unified API. Key features:

- **Model Selection**: Access to Claude (Anthropic), Nova (Amazon), Titan (Amazon), Llama (Meta), and more
- **Serverless**: No infrastructure to manage
- **Security**: IAM integration, VPC support, encryption at rest and in transit
- **Customization**: Fine-tuning, knowledge bases, and guardrails
- **Monitoring**: CloudWatch integration for metrics and logging

### What is Strands Agents?

Strands is a lightweight, code-first framework for building AI agents. Key features:

- **Simple API**: Easy to use, Pythonic interface
- **Tool Integration**: Built-in and custom tools for extending agent capabilities
- **AWS Integration**: Native support for AWS Bedrock models
- **Production Ready**: Observability, error handling, and streaming support
- **Multi-Agent**: Support for complex multi-agent systems
- **Deployment Agnostic**: Deploy on Lambda, Fargate, EKS, EC2, or AgentCore

---

## AWS Bedrock Fundamentals

### Available Models

#### Amazon Nova (Recommended for Cost-Effective Solutions)
```python
# Nova Lite - Fast, cost-effective
model = "us.amazon.nova-lite-v1:0"

# Nova Pro - Balanced performance
model = "us.amazon.nova-pro-v1:0"

# Nova Premier - Highest capability
model = "us.amazon.nova-premier-v1:0"
```

#### Claude Models (Recommended for Complex Reasoning)
```python
# Claude 4 Sonnet - Balanced
model = "us.anthropic.claude-sonnet-4-20250514"

# Claude 4 Opus - Most capable
model = "us.anthropic.claude-opus-4-20250514"

# Claude 3.5 Sonnet - Previous generation
model = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
```

### AWS Bedrock Service Endpoints

Your React app will communicate with a backend that uses these AWS services:

- **Bedrock Runtime**: `bedrock-runtime.{region}.amazonaws.com` - For model inference
- **Bedrock Agent Runtime**: `bedrock-agent-runtime.{region}.amazonaws.com` - For Knowledge Bases
- **Bedrock**: `bedrock.{region}.amazonaws.com` - For management operations

### AWS Credentials Setup

**Backend must have AWS credentials configured via:**

1. Environment variables:
```bash
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_SESSION_TOKEN=optional_session_token
AWS_DEFAULT_REGION=us-east-1
```

2. AWS CLI configuration:
```bash
aws configure
```

3. IAM roles (for AWS services like Lambda, ECS, EC2)

---

## Strands Agents Framework

### Installation

```bash
# Core framework
pip install strands-agents

# Community tools
pip install strands-agents-tools

# AWS Bedrock AgentCore integration (optional)
pip install bedrock-agentcore-runtime
```

### Basic Agent Creation

```python
from strands import Agent
from strands.tools import tool

# Simple agent with default Claude 4 Sonnet
agent = Agent()
response = agent("Tell me about AI agents")

# Agent with specific model
agent = Agent(
    model="us.amazon.nova-lite-v1:0",
    system_prompt="You are a helpful customer service assistant."
)
response = agent("How can I help you today?")
```

### Agent with Tools

```python
from strands import Agent
from strands_tools import calculator, current_time

# Create custom tool
@tool
def get_user_data(user_id: str) -> dict:
    """Fetch user data from database."""
    # Your implementation
    return {"user_id": user_id, "name": "John Doe"}

# Create agent with tools
agent = Agent(
    model="us.amazon.nova-lite-v1:0",
    tools=[calculator, current_time, get_user_data],
    system_prompt="You are a helpful assistant with access to user data and utilities."
)

# Agent automatically decides when to use tools
response = agent("What time is it and calculate 25 * 4?")
```

### Core Concepts

#### 1. Agent Loop
The agent loop is the fundamental cycle that processes input and generates responses:
1. Input Processing - Receives user input
2. Model Reasoning - LLM processes and decides on actions
3. Tool Selection - Determines if tools are needed
4. Tool Execution - Executes selected tools
5. Response Generation - Produces final response or continues reasoning

#### 2. State Management
```python
# Agent maintains conversation history
agent = Agent()
agent("My name is Alice")
response = agent("What's my name?")  # Agent remembers "Alice"

# Access and modify state
agent.state.set("user_preference", "dark_mode")
preference = agent.state.get("user_preference")
```

#### 3. Session Persistence
```python
from strands.session import FileSessionManager

# Persist sessions across restarts
agent = Agent(
    session_manager=FileSessionManager(
        session_id="user-123",
        storage_dir="./sessions"
    )
)
```

#### 4. Structured Output
```python
from pydantic import BaseModel

class UserIntent(BaseModel):
    action: str
    confidence: float
    parameters: dict

# Extract structured data
agent = Agent()
result = agent.extract(
    UserIntent,
    "I want to book a flight to New York tomorrow"
)
# result.action = "book_flight"
# result.parameters = {"destination": "New York", "date": "tomorrow"}
```

---

## Architecture Patterns

### Pattern 1: Backend API with React Frontend (Recommended)

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│  React Frontend │ HTTP │  FastAPI Backend │ SDK  │  AWS Bedrock    │
│  (JavaScript)   ├─────►│  (Python)        ├─────►│  (Strands)      │
│                 │◄─────┤  + Strands Agent │◄─────┤                 │
└─────────────────┘      └──────────────────┘      └─────────────────┘
```

**Pros:**
- Clean separation of concerns
- Python's rich AI/ML ecosystem for backend
- React's powerful UI capabilities for frontend
- Easy to scale and maintain
- Backend can handle complex agent logic

**Use Case:** Most production applications

### Pattern 2: Serverless with AWS Lambda

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│  React Frontend │ HTTP │  API Gateway     │      │  Lambda         │
│  (S3 + CloudFro)├─────►│                  ├─────►│  + Strands      │
│                 │◄─────┤                  │◄─────┤  + Bedrock SDK  │
└─────────────────┘      └──────────────────┘      └─────────────────┘
```

**Pros:**
- No server management
- Auto-scaling
- Pay per use
- High availability

**Use Case:** Event-driven apps, chatbots, APIs

### Pattern 3: AWS AgentCore Deployment

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│  React Frontend │ HTTP │  AgentCore API   │      │  AgentCore      │
│                 ├─────►│  Gateway         ├─────►│  Runtime        │
│                 │◄─────┤                  │◄─────┤  (Strands Agent)│
└─────────────────┘      └──────────────────┘      └─────────────────┘
```

**Pros:**
- Managed infrastructure
- Session isolation (dedicated microVMs)
- Built-in identity integration
- Automatic scaling
- Enhanced security

**Use Case:** Enterprise applications requiring high security and isolation

---

## Backend Integration

### FastAPI Backend Example

```python
# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from strands import Agent
from strands_tools import calculator, current_time
import uvicorn

app = FastAPI(title="AI Agent API")

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent (reuse for multiple requests)
agent = Agent(
    model="us.amazon.nova-lite-v1:0",
    tools=[calculator, current_time],
    system_prompt="You are a helpful AI assistant."
)

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    session_id: str = None

class ChatResponse(BaseModel):
    response: str
    session_id: str

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Process message with agent
        response = agent(request.message)
        
        return ChatResponse(
            response=str(response),
            session_id=request.session_id or "default"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Backend with Streaming Support

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from strands import Agent
import json

app = FastAPI()

agent = Agent(model="us.amazon.nova-lite-v1:0")

@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    async def event_generator():
        try:
            # Stream response from agent
            async for chunk in agent.stream(request.message):
                # Format as Server-Sent Events
                data = json.dumps({"content": chunk})
                yield f"data: {data}\n\n"
            
            # Send completion signal
            yield f"data: {json.dumps({'done': True})}\n\n"
            
        except Exception as e:
            error_data = json.dumps({"error": str(e)})
            yield f"data: {error_data}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

### Backend with Custom Tools

```python
from strands import Agent
from strands.tools import tool
import boto3
from typing import List, Dict

# Custom tool for AWS integration
@tool
def query_dynamodb(table_name: str, key: str) -> dict:
    """Query DynamoDB table for user data."""
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)
        response = table.get_item(Key={'id': key})
        return response.get('Item', {})
    except Exception as e:
        return {"error": str(e)}

@tool
def search_knowledge_base(query: str, kb_id: str) -> List[Dict]:
    """Search AWS Bedrock Knowledge Base."""
    try:
        client = boto3.client('bedrock-agent-runtime')
        response = client.retrieve(
            knowledgeBaseId=kb_id,
            retrievalQuery={'text': query},
            retrievalConfiguration={
                'vectorSearchConfiguration': {
                    'numberOfResults': 5
                }
            }
        )
        return response['retrievalResults']
    except Exception as e:
        return [{"error": str(e)}]

# Create agent with custom tools
agent = Agent(
    model="us.amazon.nova-lite-v1:0",
    tools=[query_dynamodb, search_knowledge_base],
    system_prompt="You have access to company database and knowledge base."
)
```

---

## React Frontend Implementation

### Basic Chat Component

```jsx
// src/components/ChatInterface.jsx
import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/chat`, {
        message: input,
        session_id: 'user-session-123'
      });

      const aiMessage = { 
        role: 'assistant', 
        content: response.data.response 
      };
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = { 
        role: 'error', 
        content: 'Failed to get response. Please try again.' 
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            <div className="message-content">{msg.content}</div>
          </div>
        ))}
        {loading && (
          <div className="message assistant">
            <div className="message-content typing">Thinking...</div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="input-area">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message..."
          disabled={loading}
        />
        <button onClick={sendMessage} disabled={loading}>
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatInterface;
```

### Streaming Chat Component

```jsx
// src/components/StreamingChat.jsx
import React, { useState, useRef, useEffect } from 'react';

const StreamingChat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [streaming, setStreaming] = useState(false);
  const eventSourceRef = useRef(null);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const sendStreamingMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setStreaming(true);

    // Create placeholder for assistant response
    const assistantMessageIndex = messages.length + 1;
    setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

    try {
      // Create EventSource for Server-Sent Events
      const eventSource = new EventSource(
        `${API_BASE_URL}/api/chat/stream?message=${encodeURIComponent(input)}`
      );
      eventSourceRef.current = eventSource;

      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.done) {
          eventSource.close();
          setStreaming(false);
        } else if (data.content) {
          // Append content to assistant message
          setMessages(prev => {
            const newMessages = [...prev];
            newMessages[assistantMessageIndex].content += data.content;
            return newMessages;
          });
        } else if (data.error) {
          console.error('Streaming error:', data.error);
          eventSource.close();
          setStreaming(false);
        }
      };

      eventSource.onerror = (error) => {
        console.error('EventSource error:', error);
        eventSource.close();
        setStreaming(false);
      };
    } catch (error) {
      console.error('Error initiating stream:', error);
      setStreaming(false);
    }
  };

  useEffect(() => {
    return () => {
      // Cleanup on unmount
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            <div className="message-content">
              {msg.content}
              {streaming && idx === messages.length - 1 && (
                <span className="cursor">▊</span>
              )}
            </div>
          </div>
        ))}
      </div>
      
      <div className="input-area">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          disabled={streaming}
        />
        <button onClick={sendStreamingMessage} disabled={streaming}>
          {streaming ? 'Streaming...' : 'Send'}
        </button>
      </div>
    </div>
  );
};

export default StreamingChat;
```

### Custom Hook for Agent Interaction

```jsx
// src/hooks/useAgent.js
import { useState, useCallback } from 'react';
import axios from 'axios';

export const useAgent = (apiUrl = 'http://localhost:8000') => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const sendMessage = useCallback(async (message, sessionId = null) => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${apiUrl}/api/chat`, {
        message,
        session_id: sessionId
      });

      return response.data;
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to send message');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [apiUrl]);

  const streamMessage = useCallback((message, onChunk, onComplete, onError) => {
    setLoading(true);
    setError(null);

    const eventSource = new EventSource(
      `${apiUrl}/api/chat/stream?message=${encodeURIComponent(message)}`
    );

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.done) {
        eventSource.close();
        setLoading(false);
        onComplete?.();
      } else if (data.content) {
        onChunk?.(data.content);
      } else if (data.error) {
        setError(data.error);
        onError?.(data.error);
        eventSource.close();
        setLoading(false);
      }
    };

    eventSource.onerror = (err) => {
      setError('Streaming error');
      onError?.(err);
      eventSource.close();
      setLoading(false);
    };

    return () => eventSource.close();
  }, [apiUrl]);

  return { sendMessage, streamMessage, loading, error };
};
```

---

## Authentication & Security

### Backend Security Best Practices

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta

app = FastAPI()
security = HTTPBearer()

SECRET_KEY = "your-secret-key"  # Use environment variable
ALGORITHM = "HS256"

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token."""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

@app.post("/api/chat")
async def chat(request: ChatRequest, user=Depends(verify_token)):
    # User is authenticated
    user_id = user.get("sub")
    agent = get_user_agent(user_id)
    response = agent(request.message)
    return {"response": str(response)}
```

### React Authentication

```jsx
// src/contexts/AuthContext.jsx
import React, { createContext, useState, useContext } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [user, setUser] = useState(null);

  const login = async (email, password) => {
    const response = await axios.post('/api/auth/login', { email, password });
    const { access_token, user } = response.data;
    
    setToken(access_token);
    setUser(user);
    localStorage.setItem('token', access_token);
    
    // Set default Authorization header
    axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
  };

  return (
    <AuthContext.Provider value={{ token, user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
```

### Environment Variables

```bash
# React (.env)
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000

# Backend (.env)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
SECRET_KEY=your-jwt-secret
DATABASE_URL=postgresql://user:pass@localhost/db
```

---

## Tools and Custom Capabilities

### Creating Custom Tools

```python
from strands.tools import tool
from typing import List, Dict
import requests

@tool
def get_weather(city: str) -> dict:
    """
    Get current weather for a city.
    
    Args:
        city: Name of the city
        
    Returns:
        Dictionary with weather information
    """
    try:
        api_key = "your_api_key"
        url = f"https://api.openweathermap.org/data/2.5/weather"
        params = {"q": city, "appid": api_key, "units": "metric"}
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        return {
            "city": city,
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"]
        }
    except Exception as e:
        return {"error": f"Failed to get weather: {str(e)}"}

@tool
def search_products(query: str, max_results: int = 5) -> List[Dict]:
    """
    Search product database.
    
    Args:
        query: Search query
        max_results: Maximum number of results to return
        
    Returns:
        List of product dictionaries
    """
    # Your database query logic
    products = []
    # ... query implementation
    return products[:max_results]

@tool
def calculate_shipping(weight: float, destination: str) -> dict:
    """
    Calculate shipping cost.
    
    Args:
        weight: Package weight in kg
        destination: Destination country code
        
    Returns:
        Dictionary with shipping cost and estimated delivery
    """
    base_rate = 10.0
    per_kg_rate = 5.0
    
    cost = base_rate + (weight * per_kg_rate)
    
    # International shipping multiplier
    if destination != "US":
        cost *= 1.5
    
    return {
        "cost": round(cost, 2),
        "currency": "USD",
        "estimated_days": 3 if destination == "US" else 7
    }
```

### Using Tools in Agents

```python
agent = Agent(
    model="us.amazon.nova-lite-v1:0",
    tools=[get_weather, search_products, calculate_shipping],
    system_prompt="""You are a helpful e-commerce assistant. 
    You can search products, check weather, and calculate shipping costs.
    Always be friendly and provide accurate information."""
)

# Agent automatically uses tools when needed
response = agent("What's the weather in New York and show me winter jackets under $100")
```

---

## Streaming & Real-time Responses

### Backend Streaming Implementation

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from strands import Agent
import asyncio
import json

app = FastAPI()
agent = Agent(model="us.amazon.nova-lite-v1:0")

@app.post("/api/chat/stream")
async def stream_chat(request: ChatRequest):
    async def generate():
        try:
            # Stream tokens as they're generated
            async for token in agent.stream(request.message):
                chunk = {
                    "type": "token",
                    "content": token,
                    "timestamp": asyncio.get_event_loop().time()
                }
                yield f"data: {json.dumps(chunk)}\n\n"
                await asyncio.sleep(0)  # Allow other tasks to run
            
            # Send completion signal
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            
        except Exception as e:
            error = {"type": "error", "message": str(e)}
            yield f"data: {json.dumps(error)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
```

### WebSocket Implementation

```python
from fastapi import WebSocket, WebSocketDisconnect
from strands import Agent

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    agent = Agent(model="us.amazon.nova-lite-v1:0")
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message = data.get("message")
            
            # Stream response
            async for token in agent.stream(message):
                await websocket.send_json({
                    "type": "token",
                    "content": token
                })
            
            # Send completion
            await websocket.send_json({"type": "done"})
            
    except WebSocketDisconnect:
        print("Client disconnected")
```

### React WebSocket Client

```jsx
import React, { useState, useEffect, useRef } from 'react';

const WebSocketChat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [connected, setConnected] = useState(false);
  const ws = useRef(null);

  useEffect(() => {
    // Connect to WebSocket
    ws.current = new WebSocket('ws://localhost:8000/ws/chat');
    
    ws.current.onopen = () => {
      console.log('WebSocket connected');
      setConnected(true);
    };
    
    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'token') {
        setMessages(prev => {
          const newMessages = [...prev];
          const lastMessage = newMessages[newMessages.length - 1];
          
          if (lastMessage?.role === 'assistant' && !lastMessage.complete) {
            lastMessage.content += data.content;
          } else {
            newMessages.push({
              role: 'assistant',
              content: data.content,
              complete: false
            });
          }
          return newMessages;
        });
      } else if (data.type === 'done') {
        setMessages(prev => {
          const newMessages = [...prev];
          newMessages[newMessages.length - 1].complete = true;
          return newMessages;
        });
      }
    };
    
    ws.current.onclose = () => {
      console.log('WebSocket disconnected');
      setConnected(false);
    };
    
    return () => {
      ws.current?.close();
    };
  }, []);

  const sendMessage = () => {
    if (!input.trim() || !connected) return;
    
    setMessages(prev => [...prev, { role: 'user', content: input }]);
    ws.current.send(JSON.stringify({ message: input }));
    setInput('');
  };

  return (
    <div className="chat-container">
      <div className="status">
        {connected ? '🟢 Connected' : '🔴 Disconnected'}
      </div>
      {/* Rest of component */}
    </div>
  );
};
```

---

## Best Practices

### 1. Error Handling

```python
# Backend
from strands import Agent
import logging

logger = logging.getLogger(__name__)

@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        agent = Agent(model="us.amazon.nova-lite-v1:0")
        response = agent(request.message)
        return {"response": str(response)}
        
    except Exception as e:
        logger.error(f"Agent error: {str(e)}", exc_info=True)
        
        # Return graceful error to user
        return {
            "response": "I'm having trouble processing that right now. Please try again.",
            "error": True
        }
```

```jsx
// Frontend
const sendMessage = async () => {
  try {
    const response = await axios.post('/api/chat', { message: input });
    // Handle success
  } catch (error) {
    if (error.response?.status === 500) {
      setError('Server error. Please try again later.');
    } else if (error.response?.status === 429) {
      setError('Too many requests. Please wait a moment.');
    } else {
      setError('An unexpected error occurred.');
    }
  }
};
```

### 2. Performance Optimization

```python
# Use connection pooling
import boto3
from botocore.config import Config

config = Config(
    max_pool_connections=50,
    retries={'max_attempts': 3}
)

bedrock = boto3.client('bedrock-runtime', config=config)

# Cache agent instances
from functools import lru_cache

@lru_cache(maxsize=100)
def get_agent(user_id: str):
    return Agent(
        model="us.amazon.nova-lite-v1:0",
        session_id=f"user-{user_id}"
    )
```

### 3. Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/chat")
@limiter.limit("10/minute")
async def chat(request: Request, chat_request: ChatRequest):
    # Handle chat
    pass
```

### 4. Monitoring and Logging

```python
from strands import Agent
import structlog

logger = structlog.get_logger()

@app.post("/api/chat")
async def chat(request: ChatRequest):
    logger.info("chat_request", 
                user_id=request.session_id, 
                message_length=len(request.message))
    
    start_time = time.time()
    response = agent(request.message)
    duration = time.time() - start_time
    
    logger.info("chat_response", 
                user_id=request.session_id,
                duration=duration,
                response_length=len(str(response)))
    
    return {"response": str(response)}
```

### 5. Cost Management

```python
# Track token usage
from strands import Agent

agent = Agent(model="us.amazon.nova-lite-v1:0")

# Monitor usage
response = agent("Your query")
if hasattr(response, 'usage'):
    input_tokens = response.usage.get('input_tokens', 0)
    output_tokens = response.usage.get('output_tokens', 0)
    
    # Log for cost tracking
    logger.info("token_usage", 
                input=input_tokens, 
                output=output_tokens,
                total=input_tokens + output_tokens)

# Use cheaper models for simple tasks
def get_model_for_task(complexity: str):
    if complexity == 'simple':
        return "us.amazon.nova-lite-v1:0"  # Cheapest
    elif complexity == 'moderate':
        return "us.amazon.nova-pro-v1:0"   # Balanced
    else:
        return "us.anthropic.claude-sonnet-4-20250514"  # Most capable
```

---

## Code Examples

### Complete E-commerce Assistant

```python
# backend/ecommerce_agent.py
from strands import Agent
from strands.tools import tool
from typing import List, Dict
import boto3

# Custom tools for e-commerce
@tool
def search_products(query: str, category: str = None, max_price: float = None) -> List[Dict]:
    """Search for products in the catalog."""
    # Database query implementation
    products = [
        {"id": 1, "name": "Laptop", "price": 999.99, "category": "electronics"},
        {"id": 2, "name": "Headphones", "price": 149.99, "category": "electronics"}
    ]
    
    # Filter by criteria
    if category:
        products = [p for p in products if p['category'] == category]
    if max_price:
        products = [p for p in products if p['price'] <= max_price]
    
    return products

@tool
def get_product_details(product_id: int) -> Dict:
    """Get detailed information about a specific product."""
    # Database lookup
    return {
        "id": product_id,
        "name": "Sample Product",
        "price": 99.99,
        "description": "High quality product",
        "in_stock": True,
        "reviews": 4.5
    }

@tool
def check_inventory(product_id: int, quantity: int = 1) -> Dict:
    """Check if product is available in requested quantity."""
    # Inventory system check
    return {
        "product_id": product_id,
        "available": True,
        "quantity_in_stock": 50,
        "can_fulfill": True
    }

@tool
def calculate_shipping(items: List[int], zip_code: str) -> Dict:
    """Calculate shipping cost and estimated delivery."""
    # Shipping calculation logic
    return {
        "cost": 9.99,
        "estimated_days": 3,
        "method": "Standard"
    }

# Create specialized agent
ecommerce_agent = Agent(
    model="us.amazon.nova-lite-v1:0",
    tools=[search_products, get_product_details, check_inventory, calculate_shipping],
    system_prompt="""You are a helpful e-commerce shopping assistant. 
    You can help customers find products, check availability, and provide shipping information.
    Always be friendly and provide accurate product information.
    If a product is out of stock, suggest alternatives."""
)

# FastAPI endpoint
from fastapi import FastAPI

app = FastAPI()

@app.post("/api/shop")
async def shop(request: ChatRequest):
    response = ecommerce_agent(request.message)
    return {"response": str(response)}
```

### Multi-Agent System

```python
# Multi-agent coordination for customer support
from strands import Agent
from strands.tools import tool

# Specialized agents
technical_agent = Agent(
    model="us.anthropic.claude-sonnet-4-20250514",
    system_prompt="You are a technical support specialist. Help with technical issues."
)

billing_agent = Agent(
    model="us.amazon.nova-lite-v1:0",
    system_prompt="You are a billing specialist. Help with payment and subscription issues."
)

general_agent = Agent(
    model="us.amazon.nova-lite-v1:0",
    system_prompt="You are a general customer service agent. Route complex issues to specialists."
)

@tool
def route_to_technical(issue_description: str) -> str:
    """Route technical issues to technical support specialist."""
    response = technical_agent(issue_description)
    return str(response)

@tool
def route_to_billing(billing_question: str) -> str:
    """Route billing questions to billing specialist."""
    response = billing_agent(billing_question)
    return str(response)

# Router agent with access to specialists
router_agent = Agent(
    model="us.amazon.nova-pro-v1:0",
    tools=[route_to_technical, route_to_billing],
    system_prompt="""You are a customer service router. 
    Analyze customer questions and route to the appropriate specialist:
    - Technical issues → route_to_technical
    - Billing/payment → route_to_billing
    - General questions → handle directly
    
    Always provide excellent customer service."""
)
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. AWS Credentials Not Found

**Error:** `NoCredentialsError: Unable to locate credentials`

**Solutions:**
```bash
# Option 1: Configure AWS CLI
aws configure

# Option 2: Environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1

# Option 3: Use IAM roles (recommended for AWS services)
```

#### 2. Model Access Denied

**Error:** `AccessDeniedException: You don't have access to the model`

**Solutions:**
1. Go to AWS Bedrock Console
2. Navigate to "Model access"
3. Request access to desired models
4. Wait for approval (usually instant for most models)

#### 3. CORS Errors in React

**Error:** `Access-Control-Allow-Origin header`

**Solution:**
```python
# Backend: Add CORS middleware
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 4. Streaming Not Working

**Issue:** Streaming response not displaying in real-time

**Solution:**
```jsx
// Ensure proper event handling
const eventSource = new EventSource(url);

eventSource.onmessage = (event) => {
  // Process immediately, don't batch
  const data = JSON.parse(event.data);
  updateUIImmediately(data);
};
```

#### 5. High Latency

**Solutions:**
- Use faster models (Nova Lite for simple tasks)
- Implement caching for repeated queries
- Use connection pooling
- Deploy backend closer to AWS region
- Consider streaming for better perceived performance

---

## Additional Resources

### Documentation
- **AWS Bedrock**: https://docs.aws.amazon.com/bedrock/
- **Strands Agents**: https://strandsagents.com/latest/
- **FastAPI**: https://fastapi.tiangolo.com/
- **React**: https://react.dev/

### Sample Code Repositories
- Strands examples on GitHub
- AWS Bedrock samples
- React + AI integration examples

### AWS Services Integration
- **DynamoDB**: For session storage
- **S3**: For file uploads/downloads
- **CloudWatch**: For monitoring
- **API Gateway**: For production APIs
- **Lambda**: For serverless deployment
- **Cognito**: For user authentication

---

## Quick Reference

### Essential Commands

```bash
# Install Strands
pip install strands-agents strands-agents-tools

# Install FastAPI
pip install fastapi uvicorn

# Install React dependencies
npm install axios

# Run FastAPI backend
uvicorn main:app --reload

# Run React frontend
npm start

# AWS CLI
aws bedrock list-foundation-models --region us-east-1
```

### Model Selection Guide

| Use Case | Model | Reason |
|----------|-------|--------|
| Simple chat | Nova Lite | Fast, cost-effective |
| E-commerce | Nova Pro | Balanced performance |
| Complex reasoning | Claude Sonnet 4 | Superior reasoning |
| Code generation | Claude Sonnet 4 | Best for code |
| Data analysis | Claude Opus 4 | Highest capability |

### Cost Optimization

1. **Use appropriate models** - Don't use Opus for simple tasks
2. **Implement caching** - Cache frequent queries
3. **Optimize prompts** - Shorter prompts = lower costs
4. **Monitor usage** - Track token consumption
5. **Use streaming** - Better UX without cost increase

---

This guide provides comprehensive context for integrating AWS Bedrock and Strands Agents into your React application. Use it as a reference when building AI-powered features, and adjust the examples to fit your specific use case.