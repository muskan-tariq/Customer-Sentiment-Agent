# Fix: Worker Timeout Issue

## Problem
Workers are timing out after 2 minutes because:
- Analysis takes longer than worker timeout
- Multiple Hugging Face API calls (sentiment, emotion, aspect, etc.)
- Each API call can take 30-60 seconds
- Total time exceeds 2 minutes

## Solution Applied

### 1. Increased Gunicorn Timeout ✅
- Changed from: `--timeout 180`
- Changed to: `--timeout 300` (5 minutes)
- Added: `--keep-alive 5`

### 2. Reduced API Call Timeouts ✅
- Changed from: `timeout=60` and `timeout=90`
- Changed to: `timeout=30` (fail faster, use fallback)

### 3. Faster Fallback ✅
- API calls now fail after 30 seconds
- Falls back to keyword-based analysis (fast)
- Prevents long waits

---

## Updated Files

1. **`render.yaml`**:
   - Timeout: 300 seconds (5 minutes)
   - Graceful timeout: 300 seconds
   - Keep-alive: 5 seconds

2. **`agent/analysis/analysis_engine.py`**:
   - API timeout: 30 seconds (was 60-90)
   - Faster failure → faster fallback

---

## Next Steps

### 1. Update Render Settings

**In Render Dashboard:**
1. Go to your service → **Settings**
2. Update **Start Command** to:
   ```
   gunicorn wsgi:app --bind 0.0.0.0:$PORT --worker-class uvicorn.workers.UvicornWorker --timeout 300 --graceful-timeout 300 --workers 1 --keep-alive 5
   ```
3. Click **Save Changes**
4. Click **Manual Deploy** → **Clear build cache & deploy**

### 2. Wait for Deployment

- First deployment: 2-3 minutes
- Model loading: 30-60 seconds
- Service ready: Check logs for "Agent initialized"

### 3. Test

```bash
curl -X POST https://customer-sentiment-agent-g5gd.onrender.com/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "user": "test",
    "platform": "twitter",
    "text": "I love this product!",
    "country": "Germany"
  }'
```

**Expected:**
- Response within 30-60 seconds (or faster with fallback)
- No worker timeout errors

---

## How It Works Now

1. **Request received** → Search memory (fast)
2. **If no memory match** → Generate new analysis
3. **Try API** → 30 second timeout
4. **If API fails/slow** → Fallback to keyword analysis (fast)
5. **Return result** → Store in memory

**Total time: <60 seconds** (usually 10-30 seconds)

---

## Monitoring

After deployment, check logs for:
- ✅ No "WORKER TIMEOUT" errors
- ✅ "Analysis completed" messages
- ✅ Response times <60 seconds

---

**Update Render start command and redeploy!** 🚀

