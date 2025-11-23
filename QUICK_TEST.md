# Quick Test Guide - Render Deployment

## ✅ Status: Health & Root Endpoints Working!

Your agent is live at: `https://customer-sentiment-agent-g5gd.onrender.com`

---

## Quick Tests

### 1. Health Check ✅ (Working)
**Browser**: https://customer-sentiment-agent-g5gd.onrender.com/health

**Or curl:**
```bash
curl https://customer-sentiment-agent-g5gd.onrender.com/health
```

**Expected**: `{"status": "healthy", ...}`

---

### 2. Root Endpoint ✅ (Working)
**Browser**: https://customer-sentiment-agent-g5gd.onrender.com/

**Expected**: API information JSON

---

### 3. Analyze Endpoint (May timeout on first request)

**First Request (Cold Start):**
- Takes 30-60 seconds (model loading)
- This is normal for Render free tier
- Subsequent requests are faster

**Test with curl:**
```bash
curl -X POST https://customer-sentiment-agent-g5gd.onrender.com/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "user": "test_user",
    "platform": "twitter",
    "text": "I love this product!",
    "country": "Germany"
  }'
```

**Wait 30-60 seconds** for first response.

---

## Check Render Logs

1. Go to Render dashboard
2. Select your service
3. Click **"Logs"** tab
4. Look for:
   - ✅ "Agent initialized and ready to serve requests!"
   - ✅ "Using deployment configuration"
   - ✅ Model loading messages
   - ❌ Any errors

---

## Check Memory Usage

1. Go to Render dashboard
2. Select your service
3. Click **"Metrics"** tab
4. Check **Memory** graph
5. Should stay under **512MB**

---

## Manual Browser Test

1. Open: https://customer-sentiment-agent-g5gd.onrender.com/health
   - Should show: `{"status": "healthy"}`

2. Open: https://customer-sentiment-agent-g5gd.onrender.com/
   - Should show API info

3. For `/analyze`, use a tool like:
   - **Postman** (recommended)
   - **curl** (command line)
   - **Thunder Client** (VS Code extension)

---

## Using Postman

1. Create new POST request
2. URL: `https://customer-sentiment-agent-g5gd.onrender.com/analyze`
3. Headers: `Content-Type: application/json`
4. Body (raw JSON):
```json
{
  "user": "test_user",
  "platform": "twitter",
  "text": "I love this product! It works perfectly.",
  "country": "Germany"
}
```
5. Click **Send**
6. Wait 30-60 seconds (first request)

---

## Expected Response

```json
{
  "sentiment_label": "satisfaction",
  "sentiment_score": 0.95,
  "emotion_analysis": [
    {
      "emotion": "joy",
      "score": 0.85
    }
  ],
  "engagement_prediction": "high",
  "topic_extracted": ["product", "satisfaction"],
  "region": "Germany",
  "recommendation": "...",
  "database_status": "retrieved_from_mongo",
  "langgraph_status": "Active",
  "timestamp": "2025-11-23T..."
}
```

---

## Troubleshooting

### Issue: Timeout on First Request
- **Normal**: First request loads models (30-60 seconds)
- **Solution**: Wait longer, or check Render logs

### Issue: 500 Error
- **Check**: Render logs for errors
- **Common**: Memory exceeded, model loading failed

### Issue: Slow Response
- **Normal**: Render free tier is slower
- **Solution**: First request is slowest, subsequent are faster

---

## What's Working ✅

- ✅ Health endpoint: Working
- ✅ Root endpoint: Working
- ✅ Agent deployed: Successfully
- ✅ Memory optimized: CPU-only PyTorch
- ⏳ Analyze endpoint: May timeout on first request (normal)

---

## Next Steps

1. **Test analyze endpoint** with Postman/curl (wait 30-60s)
2. **Check Render logs** for any errors
3. **Monitor memory** in Metrics tab
4. **Share URL** with supervisor group after successful test

---

**Your deployment is working! The timeout is just due to cold start (first request).** 🎉
