# Testing Guide - Sentiment Analysis Agent

## Quick Answer: Can it handle supervisor agent requests?

**YES!** ✅ The agent is fully capable of receiving requests from supervisor agents and responding with JSON. It uses standard HTTP REST API that any agent can call.

### Request Format (Supervisor → Sentiment Agent)

```http
POST http://localhost:8000/analyze
Content-Type: application/json

{
  "text": "Your text to analyze here"
}
```

### Response Format (Sentiment Agent → Supervisor)

```json
{
  "status": "success",
  "agent": "sentiment_agent",
  "input": "Your text to analyze here",
  "result": {
    "sentiment": {...},
    "emotion": {...},
    "aspects": {...},
    "comparison": {...},
    "summary": {...},
    "confidence": 0.85
  },
  "memory_used": false
}
```

---

## Step-by-Step Testing Guide

### Prerequisites

1. Python 3.8+ installed
2. All dependencies installed: `pip install -r requirements.txt`
3. (Optional) Hugging Face API token for faster inference

---

## Method 1: Quick Test (Recommended)

### Step 1: Start the Agent Server

Open a terminal/command prompt and run:

```bash
python main.py
```

You should see output like:
```
INFO - Starting Sentiment Analysis Agent...
INFO - Initializing vector store...
INFO - Loading embedding model: all-MiniLM-L6-v2
INFO - Embedding model loaded successfully
INFO - Initializing analysis engine...
INFO - Initializing LangGraph workflow...
INFO - Creating FastAPI application...
INFO - Starting server on 0.0.0.0:8000
```

**✅ Server is running when you see:** `Uvicorn running on http://0.0.0.0:8000`

### Step 2: Test Health Endpoint

Open a **NEW terminal/command prompt** (keep the server running) and run:

**Windows (PowerShell):**
```powershell
curl http://localhost:8000/health
```

**Windows (CMD):**
```cmd
curl http://localhost:8000/health
```

**Linux/Mac:**
```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "agent": "sentiment_agent",
  "version": "1.0.0",
  "service": "operational"
}
```

**✅ If you see this, the agent is working!**

### Step 3: Test Analyze Endpoint

**Windows (PowerShell):**
```powershell
curl -X POST http://localhost:8000/analyze -H "Content-Type: application/json" -d '{\"text\": \"I love this product!\"}'
```

**Linux/Mac:**
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "I love this product!"}'
```

**Expected Response:** JSON with sentiment analysis results

**✅ If you get JSON response, the agent is fully functional!**

---

## Method 2: Automated Test Script

### Step 1: Start the Agent Server

```bash
python main.py
```

### Step 2: Run Test Script

Open a **NEW terminal** and run:

```bash
python test_agent.py
```

This will automatically test:
- ✅ Health check endpoint
- ✅ Analyze endpoint
- ✅ Supervisor request format
- ✅ Memory system

**Expected Output:**
```
============================================================
SENTIMENT ANALYSIS AGENT - TESTING SUITE
============================================================

Testing agent at: http://localhost:8000
Make sure the server is running: python main.py

============================================================
TEST 1: Health Check
============================================================
Status Code: 200
Response: {
  "status": "healthy",
  "agent": "sentiment_agent",
  ...
}
✅ Health check PASSED

============================================================
TEST 2: Analyze Endpoint
============================================================
...
✅ Analyze endpoint PASSED

============================================================
TEST SUMMARY
============================================================
Health Check: ✅ PASSED
Analyze Endpoint: ✅ PASSED
Supervisor Request: ✅ PASSED
Memory System: ✅ PASSED

Total: 4/4 tests passed

🎉 All tests passed! Agent is working correctly.
```

---

## Method 3: Test with Supervisor Agent Example

### Step 1: Start the Agent Server

```bash
python main.py
```

### Step 2: Run Supervisor Example

Open a **NEW terminal** and run:

```bash
python supervisor_example.py
```

This demonstrates how a supervisor agent would call your sentiment agent.

**Expected Output:**
```
============================================================
SUPERVISOR AGENT EXAMPLE
============================================================

Checking sentiment agent health...
✅ Sentiment agent is healthy

Example 1: Positive Feedback
------------------------------------------------------------
Supervisor: Processing feedback...
Text: I love this product! It's amazing and works perfectly...
Supervisor: Received analysis from sentiment agent:
  - Sentiment: positive
  - Emotion: joy
  - Memory Used: False
...
```

---

## Method 4: Manual Testing with Python

### Step 1: Start the Agent Server

```bash
python main.py
```

### Step 2: Run Python Test Script

Create a file `manual_test.py`:

```python
import requests

# Test health
response = requests.get("http://localhost:8000/health")
print("Health:", response.json())

# Test analyze
response = requests.post(
    "http://localhost:8000/analyze",
    json={"text": "I love this product!"}
)
print("Analysis:", response.json())
```

Run it:
```bash
python manual_test.py
```

---

## Method 5: Test with Browser/Postman

### Step 1: Start the Agent Server

```bash
python main.py
```

### Step 2: Test Health Endpoint

Open browser and go to:
```
http://localhost:8000/health
```

You should see JSON response.

### Step 3: Test Analyze Endpoint (Use Postman or similar)

**URL:** `POST http://localhost:8000/analyze`

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "text": "I love this product! It's amazing."
}
```

**Expected:** JSON response with analysis results

---

## Troubleshooting

### Problem: "Connection refused" or "Cannot connect"

**Solution:**
- Make sure the server is running (`python main.py`)
- Check if port 8000 is already in use
- Try changing port in `config.yaml`

### Problem: "Module not found" errors

**Solution:**
```bash
pip install -r requirements.txt
```

### Problem: Slow responses

**Solution:**
- First request may be slow (loading models)
- Get free Hugging Face token: https://huggingface.co/settings/tokens
- Set it: `export HUGGINGFACE_API_TOKEN="your_token"`

### Problem: API errors

**Solution:**
- Check logs in `./logs/agent.log`
- Verify Hugging Face API token if using API mode
- Agent works without token (uses fallback)

---

## Verification Checklist

- [ ] Server starts without errors
- [ ] Health endpoint returns `{"status": "healthy"}`
- [ ] Analyze endpoint accepts POST requests
- [ ] Analyze endpoint returns JSON with `status: "success"`
- [ ] Response contains `sentiment`, `emotion`, `aspects`, `comparison`, `summary`
- [ ] Memory system works (second similar request uses memory)
- [ ] Supervisor agent can call the endpoint successfully

---

## Integration with Supervisor Agent

Your supervisor agent can call this agent like this:

```python
import requests

def call_sentiment_agent(text: str):
    response = requests.post(
        "http://localhost:8000/analyze",
        json={"text": text},
        timeout=60
    )
    return response.json()

# Usage
result = call_sentiment_agent("Customer feedback text here")
print(result["result"]["sentiment"])
```

---

## Next Steps

1. ✅ Verify agent is working using Method 1 or 2
2. ✅ Test with supervisor agent using `supervisor_example.py`
3. ✅ Integrate with your supervisor agent system
4. ✅ Monitor logs in `./logs/agent.log`

---

## Quick Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Check if agent is running |
| `/analyze` | POST | Analyze text for sentiment |
| `/` | GET | API information |

**Request Format:**
```json
{"text": "Your text here"}
```

**Response Format:**
```json
{
  "status": "success",
  "agent": "sentiment_agent",
  "input": "...",
  "result": {...},
  "memory_used": false
}
```

