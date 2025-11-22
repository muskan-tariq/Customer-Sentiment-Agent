# Free Deployment Guide - PythonAnywhere (No Credit Card Required)

## ✅ Completely Free - No Credit Card Needed!

PythonAnywhere offers a free tier that's perfect for deploying your sentiment analysis agent.

---

## Step-by-Step Deployment

### Step 1: Create PythonAnywhere Account

1. Go to: **https://www.pythonanywhere.com/**
2. Click **"Sign up for free"**
3. Create account (no credit card required)
4. Verify email if needed

---

### Step 2: Upload Your Code

**Option A: Using Git (Recommended)**

1. Push your code to GitHub (make it public or private)
2. In PythonAnywhere dashboard, go to **"Files"** tab
3. Open **"Consoles"** tab
4. Click **"Bash"** console
5. Run:
   ```bash
   cd ~
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git sentiment_agent
   cd sentiment_agent
   ```

**Option B: Upload Files Directly**

1. In PythonAnywhere dashboard, go to **"Files"** tab
2. Navigate to your home directory
3. Click **"Upload a file"**
4. Upload all your project files (or zip and extract)

---

### Step 3: Install Dependencies

1. Go to **"Consoles"** tab
2. Click **"Bash"** console
3. Navigate to your project:
   ```bash
   cd ~/sentiment_agent  # or your project folder name
   ```
4. Install dependencies:
   ```bash
   pip3.10 install --user -r requirements.txt
   ```

**Note:** PythonAnywhere uses Python 3.10 by default. Adjust if needed.

---

### Step 4: Configure Environment Variables

1. In PythonAnywhere dashboard, go to **"Files"** tab
2. Navigate to your home directory (`/home/YOUR_USERNAME/`)
3. Create/edit `.bashrc` file
4. Add environment variables:
   ```bash
   export HUGGINGFACE_API_TOKEN="your_token_here"  # Optional
   export MONGODB_URI="mongodb://localhost:27017/"  # Optional, or disable MongoDB
   ```
5. Save and reload: `source ~/.bashrc`

**Or** edit `config.yaml` directly to set values.

---

### Step 5: Create Web App

1. In PythonAnywhere dashboard, go to **"Web"** tab
2. Click **"Add a new web app"**
3. Choose **"Manual configuration"**
4. Select **Python 3.10** (or latest available)
5. Click **"Next"**

---

### Step 6: Configure Web App

1. In **"Web"** tab, find your web app
2. Click on it to configure

**Source code:**
- Set to: `/home/YOUR_USERNAME/sentiment_agent` (your project folder)

**WSGI configuration file:**
- Click the WSGI file link
- Replace content with:

```python
import sys
import os

# Add your project directory to the path
path = '/home/YOUR_USERNAME/sentiment_agent'
if path not in sys.path:
    sys.path.insert(0, path)

# Set working directory
os.chdir(path)

# Import your FastAPI app
from main import app as application

# For FastAPI on PythonAnywhere, we need to use ASGI
# But PythonAnywhere uses WSGI, so we'll use a wrapper
from fastapi.middleware.wsgi import WSGIMiddleware

# Wrap FastAPI app for WSGI
application = WSGIMiddleware(application)
```

**Important:** Actually, PythonAnywhere free tier doesn't support ASGI directly. We need to use a different approach.

---

### Step 7: Use Flask Wrapper (For Free Tier)

Since PythonAnywhere free tier uses WSGI (not ASGI), we need a wrapper. Let me create one:

---

## Alternative: Use Gunicorn with WSGI Wrapper

Actually, the easiest way is to create a simple WSGI wrapper file:

**Create `wsgi.py` in your project root:**

```python
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

# Import FastAPI app
from main import app

# WSGI application
application = app
```

But wait - FastAPI needs ASGI, not WSGI. For PythonAnywhere free tier, we have two options:

1. **Use ngrok** (temporary, but works immediately)
2. **Use Railway/Render** (free tier, but may need credit card)
3. **Use Replit** (completely free, no credit card)

Let me provide **Replit** instructions instead - it's easier and completely free!

---

## Better Option: Replit (100% Free, No Credit Card)

Replit is perfect for this - completely free, no credit card, supports FastAPI natively!

### Step 1: Create Replit Account

1. Go to: **https://replit.com/**
2. Click **"Sign up"** (use GitHub/Google/Email)
3. No credit card required!

### Step 2: Create New Repl

1. Click **"Create Repl"**
2. Choose **"Python"** template
3. Name it: `sentiment-agent`
4. Click **"Create Repl"**

### Step 3: Upload Your Code

**Option A: Git Import**
1. Click **"Import from GitHub"**
2. Enter your repo URL
3. Click **"Import"**

**Option B: Manual Upload**
1. Upload all your files to Replit
2. Or use Replit's file upload feature

### Step 4: Install Dependencies

1. In Replit, open **"Shell"** tab (bottom panel)
2. Run:
   ```bash
   pip install -r requirements.txt
   ```

### Step 5: Create `.replit` Configuration

Create `.replit` file in root:

```toml
run = "python main.py"
language = "python3"
entrypoint = "main.py"
```

### Step 6: Set Environment Variables

1. In Replit, click **"Secrets"** (lock icon in left sidebar)
2. Add secrets:
   - `HUGGINGFACE_API_TOKEN` = your token (optional)
   - `MONGODB_URI` = your MongoDB URI (optional)

### Step 7: Run and Get Public URL

1. Click **"Run"** button (green play icon)
2. Replit will start your server
3. You'll see a public URL like: `https://sentiment-agent.YOUR_USERNAME.repl.co`
4. **This is your deployment URL!**

### Step 8: Make It Always On (Optional)

1. In Replit, upgrade to **"Always On"** (free tier allows this for some time)
2. Or use **UptimeRobot** (free) to ping your Replit URL every 5 minutes to keep it awake

---

## Even Simpler: Use Ngrok (For Testing/Development)

If you just need a quick public URL for testing:

### Step 1: Install Ngrok

Download from: **https://ngrok.com/** (free, no signup needed for basic use)

### Step 2: Run Your Agent Locally

```bash
python main.py
```

### Step 3: Expose with Ngrok

In another terminal:
```bash
ngrok http 8000
```

### Step 4: Get Public URL

Ngrok will give you a URL like: `https://abc123.ngrok.io`

**This is your public URL!** Share this with your supervisor group.

**Note:** Free ngrok URLs change each time you restart. For permanent URL, sign up (still free, no credit card).

---

## Recommended: Replit (Easiest & Free)

I recommend **Replit** because:
- ✅ 100% free
- ✅ No credit card required
- ✅ Supports FastAPI natively
- ✅ Public URL immediately
- ✅ Easy to update code
- ✅ Can keep it running

---

## After Deployment

Once deployed, you'll have a URL like:
- Replit: `https://sentiment-agent.YOUR_USERNAME.repl.co`
- Ngrok: `https://abc123.ngrok.io`

**Share with supervisor group:**
```
Agent URL: https://your-url.com
Health Check: https://your-url.com/health
Analyze Endpoint: POST https://your-url.com/analyze
```

---

## Testing After Deployment

```bash
# Health check
curl https://your-url.com/health

# Test analyze
curl -X POST https://your-url.com/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "user": "user_1234",
    "platform": "twitter",
    "text": "I love this product!",
    "country": "Germany"
  }'
```

---

## Troubleshooting

### Replit Issues:
- If server stops: Click "Run" again
- If dependencies fail: Check Python version (should be 3.10+)
- If port error: Replit auto-assigns port, check `PORT` environment variable

### Ngrok Issues:
- If URL changes: That's normal for free tier
- For permanent URL: Sign up for free ngrok account

---

**Choose the method that works best for you!**

