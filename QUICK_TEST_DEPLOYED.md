# Quick Test Guide - Deployed Service

## 🚀 Fastest Way to Test

### Option 1: Use FastAPI Docs (Recommended) ⭐

1. **Open**: https://customer-sentiment-agent-g5gd.onrender.com/docs
2. **Click**: `POST /analyze` → **"Try it out"**
3. **Paste this** in Request body:
   ```json
   {
     "user": "test_user",
     "platform": "twitter",
     "text": "I love this product! It works perfectly.",
     "country": "Germany"
   }
   ```
4. **Click**: **"Execute"**
5. **Wait**: 30-60 seconds (first request)
6. **Check**: Response section below

---

## ✅ Expected Response

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
  "recommendation": "Promote this post...",
  "database_status": "retrieved_from_mongo",
  "langgraph_status": "Active",
  "timestamp": "2025-11-23T..."
}
```

---

## ✅ Validation Checklist

Check response has:
- ✅ `sentiment_label` (string)
- ✅ `sentiment_score` (number)
- ✅ `emotion_analysis` (array)
- ✅ `engagement_prediction` (string)
- ✅ `topic_extracted` (array)
- ✅ `region` (string or null)
- ✅ `recommendation` (string)
- ✅ `database_status` (string)
- ✅ `langgraph_status` (string)
- ✅ `timestamp` (string)

**Should NOT have:**
- ❌ `reasoning` (old field)
- ❌ `primary_emotion` (old field)
- ❌ `aspects` (old field)

---

## 🔧 If Request Times Out

1. **Wait longer**: First request takes 30-60 seconds
2. **Check Render logs**: Look for errors
3. **Update timeout**: In Render dashboard, set start command to:
   ```
   gunicorn wsgi:app --bind 0.0.0.0:$PORT --worker-class uvicorn.workers.UvicornWorker --timeout 300 --graceful-timeout 300 --workers 1 --keep-alive 5
   ```

---

## 📝 Test Different Scenarios

### Positive:
```json
{
  "text": "Amazing product! Highly recommend!",
  "country": "USA"
}
```

### Negative:
```json
{
  "text": "Terrible experience. Very disappointed.",
  "country": "UK"
}
```

### Mixed:
```json
{
  "text": "Good product but service needs improvement.",
  "country": "Canada"
}
```

---

**Use the docs interface at https://customer-sentiment-agent-g5gd.onrender.com/docs - it's the easiest way!** 🎉

