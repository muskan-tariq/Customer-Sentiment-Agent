# Render Build Command Fix - CPU-Only PyTorch

## Problem
PyTorch is downloading **~3GB of CUDA libraries**, exceeding Render's 512MB limit.

## Solution: Use CPU-Only PyTorch

### Update Render Build Command

In your Render dashboard, change the **Build Command** to:

```
pip install --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt
```

This installs CPU-only PyTorch (no CUDA), saving ~2.8GB!

---

## Steps

1. Go to Render dashboard
2. Select your service
3. Go to **Settings** tab
4. Find **Build Command** field
5. Change to:
   ```
   pip install --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt
   ```
6. Click **Save Changes**
7. Trigger manual redeploy

---

## Why This Works

- CPU-only PyTorch: ~200MB (vs ~900MB with CUDA)
- No CUDA libraries: 0MB (vs ~2GB)
- **Total savings: ~2.8GB**

Your agent doesn't need CUDA/GPU - it uses:
- CPU for embeddings (sentence-transformers)
- API for analysis (Hugging Face)

---

## Expected Memory After Fix

| Component | Memory |
|-----------|--------|
| CPU-only PyTorch | ~200MB |
| Embedding Model | ~100MB |
| ChromaDB | ~50MB |
| FastAPI + Dependencies | ~100MB |
| Python Runtime | ~50MB |
| **Total** | **~500MB** ✅ |

Fits perfectly in 512MB!

---

**Update the build command in Render and redeploy!** 🚀

