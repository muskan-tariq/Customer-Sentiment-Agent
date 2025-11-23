# Testing Your Deployed Service

## ✅ Your Service is Live!

**Service URL**: https://customer-sentiment-agent-g5gd.onrender.com  
**API Docs**: https://customer-sentiment-agent-g5gd.onrender.com/docs  
**Health Check**: https://customer-sentiment-agent-g5gd.onrender.com/health

---

## Method 1: Using FastAPI Docs (Easiest) ⭐

### Step 1: Open API Documentation
1. Go to: **https://customer-sentiment-agent-g5gd.onrender.com/docs**
2. You'll see the interactive API documentation

### Step 2: Test `/health` Endpoint
1. Click on **`GET /health`**
2. Click **"Try it out"**
3. Click **"Execute"**
4. **Expected Response:**
   ```json
   {
     "status": "healthy",
     "agent": "sentiment_agent",
     "version": "1.0.0",
     "service": "operational"
   }
   ```

### Step 3: Test `/analyze` Endpoint
1. Click on **`POST /analyze`**
2. Click **"Try it out"**
3. In the **Request body** field, paste:
   ```json
   {
     "user": "test_user",
     "platform": "twitter",
     "text": "I love this product! It works perfectly.",
     "country": "Germany"
   }
   ```
4. Click **"Execute"**
5. **Wait 30-60 seconds** (first request may take longer)
6. Check the **Response** section

### Step 4: Verify Response Format
**Expected Response (NEW format):**
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

**Check for:**
- ✅ All required fields present
- ✅ `sentiment_label` is a string
- ✅ `sentiment_score` is a number (-1.0 to 1.0)
- ✅ `emotion_analysis` is an array of objects
- ✅ `topic_extracted` is an array
- ✅ `region` matches input `country`
- ✅ `database_status`, `langgraph_status`, `timestamp` present
- ❌ NO old fields like `reasoning`, `primary_emotion`, `aspects`, `summary`

---

## Method 2: Using curl (Command Line)

### Test Health:
```bash
curl https://customer-sentiment-agent-g5gd.onrender.com/health
```

### Test Analyze (with timeout):
```bash
curl -X POST https://customer-sentiment-agent-g5gd.onrender.com/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "user": "test_user",
    "platform": "twitter",
    "text": "I love this product! It works perfectly.",
    "country": "Germany"
  }' \
  --max-time 300
```

**Note**: `--max-time 300` allows up to 5 minutes (for slow API responses)

---

## Method 3: Using Python Script

Run the test script:
```bash
python test_deployed_service.py
```

**Note**: If requests timeout, increase timeout in script or try again (cold start).

---

## Test Cases

### Test 1: Positive Sentiment
```json
{
  "user": "user_123",
  "platform": "twitter",
  "text": "Amazing product! Highly recommend to everyone!",
  "country": "USA"
}
```

**Expected**: `sentiment_label` = "satisfaction" or "admiration", `sentiment_score` > 0.7

### Test 2: Negative Sentiment
```json
{
  "user": "user_456",
  "platform": "twitter",
  "text": "Terrible experience. Product broke after one day.",
  "country": "UK"
}
```

**Expected**: `sentiment_label` = "disappointment" or "anger", `sentiment_score` < -0.5

### Test 3: Mixed Sentiment
```json
{
  "user": "user_789",
  "platform": "twitter",
  "text": "Good product but customer service needs improvement.",
  "country": "Canada"
}
```

**Expected**: `sentiment_label` = "neutral" or mixed, `sentiment_score` around 0.0

### Test 4: Minimal Input
```json
{
  "text": "This is great!",
  "country": "Germany"
}
```

**Expected**: Should still work with minimal fields

---

## Response Validation Checklist

For each response, verify:

### Required Fields ✅
- [ ] `sentiment_label` (string)
- [ ] `sentiment_score` (number, -1.0 to 1.0)
- [ ] `emotion_analysis` (array of objects with `emotion` and `score`)
- [ ] `engagement_prediction` (string: "high", "medium", or "low")
- [ ] `topic_extracted` (array of strings)
- [ ] `region` (string or null)
- [ ] `recommendation` (string)
- [ ] `database_status` (string)
- [ ] `langgraph_status` (string)
- [ ] `timestamp` (string, ISO format)

### Forbidden Fields ❌ (Should NOT be present)
- [ ] `reasoning` (old field)
- [ ] `primary_emotion` (old field)
- [ ] `aspects` (old field)
- [ ] `summary` (old field)
- [ ] `comparison` (old field)

---

## Troubleshooting

### Issue: Request Timeout
**Solution**: 
- Wait 30-60 seconds (normal for first request)
- Check Render logs for worker timeout errors
- Verify start command has `--timeout 300` in Render dashboard

### Issue: 422 Validation Error
**Solution**: 
- Check request format matches expected schema
- Ensure `text` field is provided
- Check JSON syntax

### Issue: 500 Internal Server Error
**Solution**: 
- Check Render logs for errors
- Verify all dependencies installed
- Check memory usage (should be <512MB)

### Issue: Wrong Response Format
**Solution**: 
- Verify `config.deployment.yaml` is being used
- Check logs for "Using deployment configuration"
- Ensure latest code is deployed

---

## Quick Test Commands

### Using curl (Windows PowerShell):
```powershell
# Health check
Invoke-RestMethod -Uri "https://customer-sentiment-agent-g5gd.onrender.com/health" -Method Get

# Analyze
$body = @{
    user = "test_user"
    platform = "twitter"
    text = "I love this product!"
    country = "Germany"
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://customer-sentiment-agent-g5gd.onrender.com/analyze" -Method Post -Body $body -ContentType "application/json"
```

### Using Python:
```python
import requests

response = requests.post(
    "https://customer-sentiment-agent-g5gd.onrender.com/analyze",
    json={
        "user": "test_user",
        "platform": "twitter",
        "text": "I love this product!",
        "country": "Germany"
    },
    timeout=300  # 5 minutes
)

print(response.json())
```

---

## Expected Response Times

- **Health Check**: <1 second
- **First Analyze Request**: 30-60 seconds (cold start)
- **Subsequent Requests**: 10-30 seconds
- **With Memory Reuse**: 5-10 seconds

---

## Share with Supervisor Group

After successful testing, share:

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

**Use the FastAPI docs interface for easiest testing!** 🎉

