# Fix: Out of Memory on Render (512MB Limit)

## Problem
Render free tier has 512MB RAM limit. The agent is exceeding this when loading the embedding model.

## Solution: Use Smallest Embedding Model

### Option 1: Use Smallest Model (Recommended)

**Updated `config.deployment.yaml`:**
- Changed from `paraphrase-MiniLM-L3-v2` (~150MB)
- To: `paraphrase-albert-small-v2` (<100MB)

This should reduce memory usage significantly.

### Option 2: Use Hugging Face API for Embeddings (No Local Model)

If Option 1 still fails, we can use Hugging Face API for embeddings instead of loading models locally. This uses 0MB for model storage (only API calls).

**To enable:**
1. Get free Hugging Face token: https://huggingface.co/settings/tokens
2. Set environment variable in Render: `HUGGINGFACE_API_TOKEN`
3. We'll need to modify `vector_store.py` to use API instead

---

## Steps to Fix

### Step 1: Update Config (Already Done)
The `config.deployment.yaml` now uses the smallest model.

### Step 2: Redeploy on Render
1. Push updated code to GitHub
2. Render will auto-redeploy
3. Or manually trigger redeploy in Render dashboard

### Step 3: Monitor Memory
- Check Render dashboard → Metrics → Memory
- Should stay under 512MB

---

## If Still Failing: Use API for Embeddings

If the smallest model still exceeds 512MB, we need to use Hugging Face API for embeddings. This requires:
1. Hugging Face API token
2. Code changes to use API instead of local model

Let me know if you need this option implemented!

---

## Current Memory Breakdown (After Fix)

| Component | Memory (Estimated) |
|-----------|-------------------|
| Embedding Model (albert-small) | ~100MB |
| ChromaDB | ~50MB |
| FastAPI + Dependencies | ~100MB |
| Python Runtime | ~100MB |
| Gunicorn | ~50MB |
| **Total** | **~400MB** ✅ |

This should fit in 512MB!

---

**Try redeploying with the updated config. If it still fails, we'll switch to API-based embeddings.**

