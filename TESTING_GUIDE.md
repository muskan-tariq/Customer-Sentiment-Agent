# Testing Your Deployed Service - Quick Guide

## 🎯 Your Service URL

**Live Service**: https://customer-sentiment-agent-g5gd.onrender.com  
**API Docs**: https://customer-sentiment-agent-g5gd.onrender.com/docs  
**Health**: https://customer-sentiment-agent-g5gd.onrender.com/health

---

## ✅ Quick Test (FastAPI Docs)

### Step 1: Open Docs
Go to: **https://customer-sentiment-agent-g5gd.onrender.com/docs**

### Step 2: Test `/analyze` Endpoint
1. Click **`POST /analyze`**
2. Click **"Try it out"**
3. Paste this in **Request body**:
   ```json
   {
     "user": "test_user",
     "platform": "twitter",
     "text": "I love this product! It works perfectly.",
     "country": "Germany"
   }
   ```
4. Click **"Execute"**
5. **Wait 10-30 seconds** (should be faster now with fallbacks!)
6. Check **Response** section

---

## ✅ Expected Response

Your response should have **ALL** these fields:

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

## ✅ Validation Checklist

**Check for these fields:**
- [ ] `sentiment_label` (string)
- [ ] `sentiment_score` (number, -1.0 to 1.0)
- [ ] `emotion_analysis` (array of objects with `emotion` and `score`)
- [ ] `engagement_prediction` (string: "high", "medium", or "low")
- [ ] `topic_extracted` (array of strings)
- [ ] `region` (string or null - should match your input `country`)
- [ ] `recommendation` (string)
- [ ] `database_status` (string)
- [ ] `langgraph_status` (string)
- [ ] `timestamp` (string, ISO format)

**Should NOT have:**
- [ ] `reasoning` (old field - should be removed)
- [ ] `primary_emotion` (old field - should be removed)
- [ ] `aspects` (old field - should be removed)
- [ ] `summary` (old field - should be removed)

---

## 🔧 If You Get 502 Error

The fixes are applied, but you need to:

1. **Push changes to GitHub** (if not done)
2. **Wait for Render to redeploy** (check Render dashboard)
3. **Update Start Command** in Render (if not updated):
   ```
   gunicorn wsgi:app --bind 0.0.0.0:$PORT --worker-class uvicorn.workers.UvicornWorker --timeout 300 --graceful-timeout 300 --workers 1 --keep-alive 5
   ```
4. **Test again** after deployment completes

---

## 📝 Test Different Scenarios

### Positive Sentiment:
```json
{
  "text": "Amazing product! Highly recommend!",
  "country": "USA"
}
```

### Negative Sentiment:
```json
{
  "text": "Terrible experience. Very disappointed.",
  "country": "UK"
}
```

### Mixed Sentiment:
```json
{
  "text": "Good product but service needs improvement.",
  "country": "Canada"
}
```

---

## 🎉 Success Indicators

✅ **Response received** within 30 seconds  
✅ **All required fields** present  
✅ **No old fields** in response  
✅ **`region` matches** input `country`  
✅ **Valid JSON** format  

---

## 📤 Share with Supervisor Group

After successful testing:

```
Agent URL: https://customer-sentiment-agent-g5gd.onrender.com
API Docs: https://customer-sentiment-agent-g5gd.onrender.com/docs
Health: GET https://customer-sentiment-agent-g5gd.onrender.com/health
Analyze: POST https://customer-sentiment-agent-g5gd.onrender.com/analyze

Request Format:
{
  "user": "user_id",
  "platform": "twitter",
  "text": "Your text here",
  "country": "Country"
}

Response Format:
{
  "sentiment_label": "...",
  "sentiment_score": 0.95,
  "emotion_analysis": [...],
  "engagement_prediction": "high",
  "topic_extracted": [...],
  "region": "Country",
  "recommendation": "...",
  "database_status": "retrieved_from_mongo",
  "langgraph_status": "Active",
  "timestamp": "..."
}
```

---

**Use the docs interface - it's the easiest way to test!** 🚀
