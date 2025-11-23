# Render Deployment - Start Command & Steps

## 🚀 Quick Start Command

**Your Start Command for Render:**
```
gunicorn wsgi:app --bind 0.0.0.0:$PORT --worker-class uvicorn.workers.UvicornWorker --timeout 120
```

---

## 📋 Step-by-Step Deployment

### Step 1: Push Code to GitHub

1. Make sure all your files are committed
2. Push to GitHub (public or private repo)

### Step 2: Create Render Account

1. Go to: **https://dashboard.render.com/**
2. Sign up (free, no credit card needed)
3. Connect your GitHub account

### Step 3: Create New Web Service

1. In Render dashboard, click **"New +"** button
2. Select **"Web Service"**
3. Connect your GitHub repository
4. Select the repository with your agent code

### Step 4: Configure Service

Fill in these settings:

**Basic Settings:**
- **Name**: `sentiment-agent` (or your choice)
- **Region**: Choose closest to you
- **Branch**: `main` (or your default branch)
- **Root Directory**: Leave empty (or `.` if needed)

**Build & Deploy:**
- **Environment**: `Python 3`
- **Build Command**: 
  ```
  pip install -r requirements.txt
  ```
- **Start Command**: 
  ```
  gunicorn wsgi:app --bind 0.0.0.0:$PORT --worker-class uvicorn.workers.UvicornWorker --timeout 120
  ```

**Environment Variables** (click "Add Environment Variable"):
- `HUGGINGFACE_API_TOKEN` = `your_token_here` (optional, but recommended)
  - Get free token: https://huggingface.co/settings/tokens
- `MONGODB_URI` = Leave empty (MongoDB is disabled by default)

**Note**: `PORT` is automatically set by Render - don't add it manually!

### Step 5: Deploy

1. Click **"Create Web Service"**
2. Render will start building (takes 5-10 minutes)
3. Watch the build logs for progress

### Step 6: Get Your URL

Once deployment completes, you'll see:
- **Your URL**: `https://sentiment-agent.onrender.com` (or similar)
- Copy this URL - this is your agent's public endpoint!

---

## ✅ Verify Deployment

### Test Health Endpoint:
```bash
curl https://your-app.onrender.com/health
```

Expected response:
```json
{"status": "healthy", "agent": "sentiment_agent", "version": "1.0.0", "service": "operational"}
```

### Test Analyze Endpoint:
```bash
curl -X POST https://your-app.onrender.com/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "user": "test_user",
    "platform": "twitter",
    "text": "I love this product! It works perfectly.",
    "country": "Germany"
  }'
```

---

## 📝 Important Notes

### Start Command Breakdown:
- `gunicorn` - Production WSGI server
- `wsgi:app` - Points to `wsgi.py` file, `app` variable
- `--bind 0.0.0.0:$PORT` - Bind to all interfaces, use Render's PORT
- `--worker-class uvicorn.workers.UvicornWorker` - ASGI worker for FastAPI
- `--timeout 120` - 2 minute timeout (for model loading)

### Files Required:
- ✅ `wsgi.py` - WSGI entry point (already created)
- ✅ `requirements.txt` - Dependencies (includes gunicorn)
- ✅ `config.deployment.yaml` - Optimized config (auto-detected)
- ✅ `render.yaml` - Optional Render config file

### Memory Optimization:
- Your agent uses ~400MB RAM (fits in 512MB free tier)
- Uses lightweight embedding model
- Local models disabled (uses API instead)

---

## 🔧 Troubleshooting

### Build Fails:
- Check build logs in Render dashboard
- Ensure all dependencies are in `requirements.txt`
- Verify Python version (Render uses Python 3.11+)

### Service Won't Start:
- Check start command is exactly as shown above
- Verify `wsgi.py` exists and has `app` variable
- Check logs in Render dashboard

### Out of Memory:
- Already optimized, but if issues occur:
  - Use smaller model: `paraphrase-albert-small-v2`
  - Or disable embeddings entirely

### API Errors:
- Make sure `HUGGINGFACE_API_TOKEN` is set (optional but recommended)
- Check Hugging Face API status

---

## 📤 Share with Supervisor Group

After successful deployment, share:

```
Agent Name: Sentiment Analysis Agent
Base URL: https://your-app.onrender.com

Endpoints:
- Health: GET https://your-app.onrender.com/health
- Analyze: POST https://your-app.onrender.com/analyze

Request Format:
{
  "user": "user_1234",
  "platform": "twitter",
  "text": "Your text here",
  "country": "Germany"
}

Response Format:
{
  "sentiment_label": "...",
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

## 🎉 That's It!

Your agent is now deployed and ready to use!

**Your Start Command (copy this):**
```
gunicorn wsgi:app --bind 0.0.0.0:$PORT --worker-class uvicorn.workers.UvicornWorker --timeout 120
```

