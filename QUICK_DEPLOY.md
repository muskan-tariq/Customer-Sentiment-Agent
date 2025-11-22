# Quick Deployment - Replit (100% Free, No Credit Card)

## Fastest Way to Deploy Your Agent

### Step 1: Create Replit Account
1. Go to: **https://replit.com/**
2. Sign up (free, no credit card)

### Step 2: Create New Repl
1. Click **"Create Repl"**
2. Choose **"Python"**
3. Name: `sentiment-agent`
4. Click **"Create"**

### Step 3: Upload Code
**Option A: Git Import**
- Click **"Import from GitHub"**
- Paste your repo URL
- Click **"Import"**

**Option B: Manual Upload**
- Drag and drop all your project files into Replit

### Step 4: Install Dependencies
In Replit Shell (bottom panel):
```bash
pip install -r requirements.txt
```

### Step 5: Set Secrets (Optional)
1. Click **"Secrets"** (lock icon)
2. Add:
   - `HUGGINGFACE_API_TOKEN` (optional)
   - `MONGODB_URI` (optional, or disable in config.yaml)

### Step 6: Run
1. Click **"Run"** button (green play icon)
2. Wait for: `Uvicorn running on http://0.0.0.0:8000`
3. Copy your public URL (shown in Replit)

### Step 7: Share URL
Your URL will be: `https://sentiment-agent.YOUR_USERNAME.repl.co`

**Share this with your supervisor group:**
- Health: `https://your-url.repl.co/health`
- Analyze: `POST https://your-url.repl.co/analyze`

---

## Keep It Running

**Free Replit goes to sleep after inactivity. To keep it awake:**

1. **Option 1:** Use UptimeRobot (free)
   - Sign up: https://uptimerobot.com/
   - Add monitor for your Replit URL
   - Set to ping every 5 minutes

2. **Option 2:** Upgrade Replit (still free tier available)

---

## Test Your Deployment

```bash
# Health check
curl https://your-url.repl.co/health

# Test analyze
curl -X POST https://your-url.repl.co/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "user": "test_user",
    "platform": "twitter",
    "text": "I love this product!",
    "country": "Germany"
  }'
```

---

**That's it! Your agent is now publicly accessible!** 🎉

