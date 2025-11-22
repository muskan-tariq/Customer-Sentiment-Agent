# Deployment Guide - Completely Free (No Credit Card)

## 🎯 Quick Answer: Which API Does Your Agent Use?

When you send data to your agent, it uses:
- **FastAPI** (Python web framework) - Your main API server
- **Endpoint**: `POST /analyze` 
- **Location**: `agent/api/api_server.py`

The agent processes requests through:
1. FastAPI receives request → `agent/api/api_server.py`
2. LangGraph workflow → `agent/workflow/agent_workflow.py`
3. Analysis engine → `agent/analysis/analysis_engine.py`
4. Vector memory → `agent/memory/vector_store.py`
5. Returns JSON response

---

## 🚀 Free Deployment Options (No Credit Card)

### Option 1: Replit (Recommended - Easiest)

**100% Free, No Credit Card Required!**

#### Steps:

1. **Sign up**: https://replit.com/ (free account)

2. **Create Repl**:
   - Click "Create Repl"
   - Choose "Python" template
   - Name: `sentiment-agent`

3. **Upload Code**:
   - Option A: Click "Import from GitHub" (if your code is on GitHub)
   - Option B: Drag and drop all files into Replit

4. **Install Dependencies**:
   - Open Shell (bottom panel)
   - Run: `pip install -r requirements.txt`

5. **Set Environment Variables** (Optional):
   - Click "Secrets" (lock icon)
   - Add: `HUGGINGFACE_API_TOKEN` (optional)

6. **Run**:
   - Click "Run" button
   - Wait for server to start
   - Copy your public URL (e.g., `https://sentiment-agent.USERNAME.repl.co`)

7. **Share URL**:
   - Your agent is now live at: `https://your-url.repl.co`
   - Health: `https://your-url.repl.co/health`
   - Analyze: `POST https://your-url.repl.co/analyze`

**That's it!** Your supervisor group can now use your agent.

---

### Option 2: Ngrok (For Quick Testing)

**Free, No Signup Needed (for basic use)**

1. **Download Ngrok**: https://ngrok.com/download

2. **Run Your Agent Locally**:
   ```bash
   python main.py
   ```

3. **Expose with Ngrok** (new terminal):
   ```bash
   ngrok http 8000
   ```

4. **Get Public URL**:
   - Ngrok shows: `https://abc123.ngrok.io`
   - This is your public URL!

**Note**: Free ngrok URLs change each restart. For permanent URL, sign up (still free, no credit card).

---

### Option 3: PythonAnywhere (Free Tier)

**Free, No Credit Card Required**

1. Sign up: https://www.pythonanywhere.com/
2. Upload code via Files tab
3. Create web app (Manual configuration)
4. Configure WSGI file
5. Get public URL

**Note**: Free tier has some limitations, but works for your agent.

---

## 📋 What Your Supervisor Group Needs

After deployment, share this information:

```
Agent Name: Sentiment Analysis Agent
Base URL: https://your-deployed-url.com

Endpoints:
- Health Check: GET https://your-url.com/health
- Analyze: POST https://your-url.com/analyze

Request Format:
{
  "user": "user_1234",
  "platform": "twitter",
  "timestamp": "2025-10-21T13:45:00Z",
  "text": "Your text here",
  "hashtags": ["tag1"],
  "likes": 100,
  "retweets": 50,
  "country": "Germany"
}

Response Format:
{
  "sentiment_label": "admiration",
  "sentiment_score": 0.94,
  "emotion_analysis": [...],
  "engagement_prediction": "high",
  "topic_extracted": [...],
  "region": "Germany",
  "recommendation": "...",
  "database_status": "retrieved_from_mongo",
  "langgraph_status": "Active",
  "timestamp": "2025-10-21T13:45:00Z"
}
```

---

## ✅ Testing After Deployment

```bash
# Health check
curl https://your-url.com/health

# Test analyze
curl -X POST https://your-url.com/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "user": "test",
    "platform": "twitter",
    "text": "I love this product!",
    "country": "Germany"
  }'
```

---

## 🔧 Configuration for Deployment

**Before deploying, check `config.yaml`:**

- MongoDB: Set `enabled: false` if you don't have MongoDB
- API Port: Will use `PORT` environment variable (cloud platforms set this automatically)
- Logging: File logging may not work on cloud - that's okay, console logs work

---

## 📝 Files Created for Deployment

- `DEPLOYMENT_GUIDE.md` - Detailed deployment instructions
- `QUICK_DEPLOY.md` - Quick Replit deployment guide
- `.replit` - Replit configuration
- `replit.nix` - Replit dependencies
- `main.py` - Updated to use `PORT` environment variable

---

## 🎉 Recommended: Use Replit

**Why Replit?**
- ✅ 100% free
- ✅ No credit card
- ✅ FastAPI works natively
- ✅ Public URL immediately
- ✅ Easy to update code
- ✅ Can keep running

**Just follow `QUICK_DEPLOY.md` - it's the fastest way!**

---

## After Deployment

Once deployed, your supervisor group can integrate like this:

```python
import requests

def call_sentiment_agent(text, user_data):
    response = requests.post(
        "https://your-deployed-url.com/analyze",
        json={
            "user": user_data.get("user"),
            "platform": user_data.get("platform"),
            "text": text,
            "country": user_data.get("country")
        }
    )
    return response.json()
```

**Your agent is ready for integration!** 🚀

