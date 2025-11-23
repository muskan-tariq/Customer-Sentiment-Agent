# Troubleshooting 502 Bad Gateway on Render

## Problem
You're seeing a **502 Bad Gateway** error, which means:
- Your service is deployed
- But it's not responding to requests
- Render can't reach your application

---

## Step 1: Check Render Logs

1. Go to Render dashboard
2. Select your service: `customer-sentiment-agent-g5gd`
3. Click **"Logs"** tab
4. Look for:
   - ❌ **Errors** (red text)
   - ❌ **"Out of memory"**
   - ❌ **"Application failed to start"**
   - ❌ **Port binding errors**
   - ✅ **"Agent initialized and ready to serve requests!"** (good sign)

---

## Step 2: Common Causes & Fixes

### Issue 1: Service Still Starting (Cold Start)
**Symptoms:**
- Logs show "Loading embedding model..."
- Takes 30-60 seconds

**Fix:**
- Wait 1-2 minutes
- Try again

---

### Issue 2: Out of Memory
**Symptoms:**
- Logs show "Out of memory (used over 512Mi)"
- Service crashes during startup

**Fix:**
- Verify build command uses CPU-only PyTorch:
  ```
  pip install --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt
  ```
- Check `config.deployment.yaml` uses smallest model:
  ```yaml
  embeddings:
    model: "sentence-transformers/paraphrase-albert-small-v2"
  ```

---

### Issue 3: Port Binding Issue
**Symptoms:**
- Logs show "No open ports detected"
- Service starts but doesn't bind to PORT

**Fix:**
- Verify start command:
  ```
  gunicorn wsgi:app --bind 0.0.0.0:$PORT --worker-class uvicorn.workers.UvicornWorker --timeout 120
  ```
- Make sure `$PORT` is in the command (Render sets this automatically)

---

### Issue 4: Application Crashed
**Symptoms:**
- Logs show Python errors/tracebacks
- Service starts then immediately stops

**Fix:**
- Check logs for specific error
- Common issues:
  - Missing dependencies
  - Import errors
  - Configuration errors

---

### Issue 5: Timeout During Startup
**Symptoms:**
- Service takes too long to start
- Render kills it before ready

**Fix:**
- Increase timeout in start command:
  ```
  gunicorn wsgi:app --bind 0.0.0.0:$PORT --worker-class uvicorn.workers.UvicornWorker --timeout 180 --graceful-timeout 180
  ```

---

## Step 3: Verify Configuration

### Check Build Command:
```
pip install --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt
```

### Check Start Command:
```
gunicorn wsgi:app --bind 0.0.0.0:$PORT --worker-class uvicorn.workers.UvicornWorker --timeout 120
```

### Check Environment Variables:
- `HUGGINGFACE_API_TOKEN` (optional)
- `MONGODB_URI` (optional, leave empty if disabled)

---

## Step 4: Manual Restart

1. Go to Render dashboard
2. Select your service
3. Click **"Manual Deploy"** → **"Clear build cache & deploy"**
4. Wait for deployment to complete
5. Check logs again

---

## Step 5: Test After Fix

Once service is running, test:

```bash
# Health check
curl https://customer-sentiment-agent-g5gd.onrender.com/health

# Analyze endpoint
curl -X POST https://customer-sentiment-agent-g5gd.onrender.com/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "user": "test",
    "platform": "twitter",
    "text": "I love this product!",
    "country": "Germany"
  }'
```

---

## Quick Diagnostic Checklist

- [ ] Check Render logs for errors
- [ ] Verify build command uses CPU-only PyTorch
- [ ] Verify start command includes `$PORT`
- [ ] Check memory usage (should be <512MB)
- [ ] Wait 1-2 minutes for cold start
- [ ] Try manual restart with cleared cache

---

## If Still Failing

**Share the logs** from Render dashboard and I can help diagnose the specific issue!

Common log patterns to look for:
- `Out of memory` → Memory issue
- `ModuleNotFoundError` → Missing dependency
- `Address already in use` → Port issue
- `No module named 'wsgi'` → File structure issue

---

**Check your Render logs first - that will tell us exactly what's wrong!**

