# Render Deployment Guide (512MB RAM Optimized)

## ✅ Memory Optimizations Applied

Your agent is now optimized for Render's 512MB RAM free tier:

1. **Lightweight Embedding Model**: `paraphrase-MiniLM-L3-v2` (<150MB)
2. **Disabled Local Models**: Uses Hugging Face API instead (saves ~300MB)
3. **MongoDB Disabled**: Saves additional memory

**Total Memory Usage**: ~400MB (fits in 512MB!) ✅

---

## Deployment Steps

### Step 1: Push to GitHub

1. Push your code to GitHub (public or private)

### Step 2: Create Render Web Service

1. Go to: **https://dashboard.render.com/**
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:

**Settings:**
- **Name**: `sentiment-agent` (or your choice)
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn wsgi:app --bind 0.0.0.0:$PORT --worker-class uvicorn.workers.UvicornWorker --timeout 120`

**Environment Variables:**
- `PORT` - Auto-set by Render (don't add manually)
- `HUGGINGFACE_API_TOKEN` - Optional (get free token from https://huggingface.co/settings/tokens)
- `MONGODB_URI` - Optional (leave empty if MongoDB disabled)

### Step 3: Deploy

1. Click **"Create Web Service"**
2. Render will build and deploy automatically
3. Wait for deployment to complete (~5-10 minutes)

### Step 4: Get Your URL

Once deployed, you'll get a URL like:
- `https://sentiment-agent.onrender.com`

**This is your public agent URL!**

---

## Configuration Files

**For Deployment:**
- Use `config.deployment.yaml` (automatically detected)
- Or ensure `config.yaml` has:
  - Lightweight embedding model
  - `use_local_models: false`

---

## Testing

```bash
# Health check
curl https://your-app.onrender.com/health

# Test analyze
curl -X POST https://your-app.onrender.com/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "user": "test",
    "platform": "twitter",
    "text": "I love this product!",
    "country": "Germany"
  }'
```

---

## Memory Monitoring

1. In Render dashboard, go to **"Metrics"** tab
2. Check **"Memory"** graph
3. Should stay under 512MB

If you see memory issues:
- Use even smaller model: `paraphrase-albert-small-v2`
- Or disable embeddings entirely (use API for everything)

---

## Troubleshooting

### Issue: Still getting "Out of Memory"

**Solution 1**: Use smallest model
```yaml
embeddings:
  model: "sentence-transformers/paraphrase-albert-small-v2"
```

**Solution 2**: Disable local models completely
```yaml
huggingface:
  use_local_models: false
  use_api: true
```

**Solution 3**: Use Hugging Face API for embeddings too
- Get API token
- Set `HUGGINGFACE_API_TOKEN` environment variable
- Agent will use API instead of loading models

---

## Share with Supervisor Group

After successful deployment:

```
Agent URL: https://your-app.onrender.com
Health: GET https://your-app.onrender.com/health
Analyze: POST https://your-app.onrender.com/analyze

Request Format: (same as before)
Response Format: (same as before)
```

---

**Your agent is now optimized and ready for Render deployment!** 🚀

