# Testing Your Render Deployment

## ✅ Your Agent is Live!

**URL**: `https://customer-sentiment-agent-g5gd.onrender.com`

---

## Step 1: Health Check

### Test in Browser:
Open: `https://customer-sentiment-agent-g5gd.onrender.com/health`

**Expected Response:**
```json
{
  "status": "healthy",
  "agent": "sentiment_agent",
  "version": "1.0.0",
  "service": "operational"
}
```

### Test with curl:
```bash
curl https://customer-sentiment-agent-g5gd.onrender.com/health
```

---

## Step 2: Root Endpoint

### Test in Browser:
Open: `https://customer-sentiment-agent-g5gd.onrender.com/`

**Expected Response:**
```json
{
  "message": "Sentiment Analysis Agent API",
  "endpoints": {
    "/analyze": "POST - Analyze text for sentiment, emotion, aspects, comparison, and summary",
    "/health": "GET - Health check endpoint"
  },
  "version": "1.0.0"
}
```

---

## Step 3: Test Analyze Endpoint

### Test with curl:
```bash
curl -X POST https://customer-sentiment-agent-g5gd.onrender.com/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "user": "test_user",
    "platform": "twitter",
    "text": "I love this product! It works perfectly and exceeded my expectations.",
    "country": "Germany"
  }'
```

### Expected Response Format:
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

## Step 4: Test Multiple Scenarios

### Positive Sentiment:
```bash
curl -X POST https://customer-sentiment-agent-g5gd.onrender.com/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "user": "user_123",
    "platform": "twitter",
    "text": "Amazing service! Highly recommend to everyone!",
    "country": "USA"
  }'
```

### Negative Sentiment:
```bash
curl -X POST https://customer-sentiment-agent-g5gd.onrender.com/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "user": "user_456",
    "platform": "twitter",
    "text": "Terrible experience. The product broke after one day.",
    "country": "UK"
  }'
```

### Mixed Sentiment:
```bash
curl -X POST https://customer-sentiment-agent-g5gd.onrender.com/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "user": "user_789",
    "platform": "twitter",
    "text": "Good product but customer service needs improvement.",
    "country": "Canada"
  }'
```

---

## Step 5: Check Memory Usage

1. Go to Render dashboard
2. Select your service
3. Click **"Metrics"** tab
4. Check **Memory** graph
5. Should stay under **512MB**

---

## Step 6: Verify Response Schema

Check that response includes ALL required fields:
- ✅ `sentiment_label`
- ✅ `sentiment_score`
- ✅ `emotion_analysis` (array)
- ✅ `engagement_prediction`
- ✅ `topic_extracted` (array)
- ✅ `region`
- ✅ `recommendation`
- ✅ `database_status`
- ✅ `langgraph_status`
- ✅ `timestamp`

---

## Step 7: Test Memory Reuse

Send the same query twice - second time should be faster (memory reuse):

```bash
# First request (new analysis)
curl -X POST https://customer-sentiment-agent-g5gd.onrender.com/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "user": "test",
    "platform": "twitter",
    "text": "This is a great product!",
    "country": "Germany"
  }'

# Second request (should reuse memory)
curl -X POST https://customer-sentiment-agent-g5gd.onrender.com/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "user": "test",
    "platform": "twitter",
    "text": "This is a great product!",
    "country": "Germany"
  }'
```

---

## Step 8: Check Logs

1. Go to Render dashboard
2. Select your service
3. Click **"Logs"** tab
4. Look for:
   - ✅ "Agent initialized and ready to serve requests!"
   - ✅ "Using deployment configuration"
   - ✅ No memory errors
   - ✅ No API errors

---

## Common Issues & Fixes

### Issue: 405 Method Not Allowed
- **Cause**: Using GET instead of POST for `/analyze`
- **Fix**: Use POST method

### Issue: 500 Internal Server Error
- **Cause**: Agent initialization failed
- **Fix**: Check logs for errors

### Issue: Timeout
- **Cause**: Model loading taking too long
- **Fix**: Normal on first request, should be faster after

### Issue: Memory Exceeded
- **Cause**: Still using CUDA PyTorch
- **Fix**: Verify build command uses CPU-only PyTorch

---

## Quick Test Script

Save this as `test_deployment.sh`:

```bash
#!/bin/bash

URL="https://customer-sentiment-agent-g5gd.onrender.com"

echo "Testing Health Endpoint..."
curl -s "$URL/health" | jq .

echo -e "\n\nTesting Analyze Endpoint..."
curl -s -X POST "$URL/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "user": "test_user",
    "platform": "twitter",
    "text": "I love this product! It works perfectly.",
    "country": "Germany"
  }' | jq .

echo -e "\n\nDone!"
```

Run: `chmod +x test_deployment.sh && ./test_deployment.sh`

---

## Share with Supervisor Group

After successful testing, share:

```
Agent URL: https://customer-sentiment-agent-g5gd.onrender.com
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

**Your agent is deployed and ready to use!** 🎉

