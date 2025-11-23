# Fix: Out of Memory on Render - Immediate Solution

## Problem
Render free tier (512MB RAM) is exceeded when loading embedding model.

## Solution Applied

### 1. Switched to Smallest Model ✅
- **Before**: `paraphrase-MiniLM-L3-v2` (~150MB)
- **After**: `paraphrase-albert-small-v2` (<100MB)

### 2. Added Memory-Efficient Loading ✅
- Added `low_cpu_mem_usage=True` flag
- Explicitly set `device='cpu'`
- Added fallback for compatibility

### 3. Updated Config Files ✅
- `config.deployment.yaml` - Uses smallest model
- `config.yaml` - Updated default
- `agent/memory/vector_store.py` - Memory-efficient loading

---

## Next Steps

### 1. Commit and Push Changes
```bash
git add .
git commit -m "Optimize memory: use smallest embedding model"
git push
```

### 2. Redeploy on Render
- Render will auto-detect changes and redeploy
- Or manually trigger redeploy in dashboard

### 3. Monitor Memory
- Check Render dashboard → Metrics → Memory
- Should now stay under 512MB

---

## If Still Failing: Alternative Solution

If the smallest model still exceeds 512MB, we have two options:

### Option A: Disable Vector Memory (Temporary)
- Remove ChromaDB/embeddings entirely
- Agent will work but won't have memory reuse
- Saves ~150MB RAM

### Option B: Use Hugging Face API for Embeddings
- No local model loading (0MB for model)
- Requires Hugging Face API token
- Uses API calls for embeddings

**Let me know if you need Option A or B implemented!**

---

## Expected Memory After Fix

| Component | Memory |
|-----------|--------|
| Embedding Model (albert-small) | ~100MB |
| ChromaDB | ~50MB |
| FastAPI + Dependencies | ~100MB |
| Python Runtime | ~100MB |
| Gunicorn | ~50MB |
| **Total** | **~400MB** ✅ |

This should fit in 512MB!

---

**Push the changes and redeploy. The agent should now work on Render!** 🚀

