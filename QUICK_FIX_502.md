# Quick Fix for 502 Bad Gateway

## Immediate Steps

### 1. Check Render Logs (Most Important!)

1. Go to: https://dashboard.render.com/
2. Click your service: `customer-sentiment-agent-g5gd`
3. Click **"Logs"** tab
4. **Copy the last 50-100 lines** and check for:
   - ❌ "Out of memory"
   - ❌ Python errors/tracebacks
   - ❌ "No module named..."
   - ✅ "Agent initialized and ready to serve requests!" (good!)

---

### 2. Update Start Command in Render

1. Go to Render dashboard → Your service → **Settings**
2. Find **Start Command**
3. Change to:
   ```
   gunicorn wsgi:app --bind 0.0.0.0:$PORT --worker-class uvicorn.workers.UvicornWorker --timeout 180 --graceful-timeout 180 --workers 1
   ```
4. Click **Save Changes**
5. Click **Manual Deploy** → **Clear build cache & deploy**

---

### 3. Verify Build Command

Make sure it's:
```
pip install --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt
```

---

### 4. Wait for Cold Start

- First deployment: **2-3 minutes** (model loading)
- Subsequent requests: **30-60 seconds** (cold start)
- After warm: **<5 seconds**

---

## Most Likely Issues

### Issue 1: Out of Memory
**If logs show "Out of memory":**
- Verify build command uses CPU-only PyTorch (see above)
- Check `config.deployment.yaml` uses smallest model

### Issue 2: Service Still Starting
**If logs show "Loading embedding model...":**
- This is normal! Wait 1-2 minutes
- Service needs time to load models

### Issue 3: Application Crashed
**If logs show Python errors:**
- Share the error message
- Common: Missing dependencies, import errors

---

## Test After Fix

Wait 2-3 minutes after deployment, then:

```bash
curl https://customer-sentiment-agent-g5gd.onrender.com/health
```

Should return:
```json
{"status": "healthy", "agent": "sentiment_agent", "version": "1.0.0", "service": "operational"}
```

---

## What to Share

If still failing, share:
1. **Last 50 lines of Render logs**
2. **Build command** (from Settings)
3. **Start command** (from Settings)
4. **Memory usage** (from Metrics tab)

---

**Check your Render logs first - that will tell us exactly what's wrong!**

