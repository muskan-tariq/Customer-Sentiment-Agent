# Memory Optimization for 512MB RAM (Render Free Tier)

## Problem
Render free tier has **512MB RAM limit**. The agent was using too much memory with default models.

## Solution Applied

### 1. Lightweight Embedding Model ✅
**Changed in `config.yaml`:**
- **Before**: `all-MiniLM-L6-v2` (~250MB RAM)
- **After**: `sentence-transformers/paraphrase-MiniLM-L3-v2` (<150MB RAM)

### 2. Disabled Local Transformer Models ✅
**Changed in `config.yaml`:**
- **Before**: `use_local_models: true` (loads sentiment + emotion models = ~300MB)
- **After**: `use_local_models: false` (uses Hugging Face API instead, saves ~300MB)

**Result**: Agent now uses **<150MB RAM** for embeddings + API calls instead of local models.

---

## Memory Breakdown (After Optimization)

| Component | Memory Usage |
|-----------|--------------|
| Embedding Model (paraphrase-MiniLM-L3-v2) | ~150MB |
| ChromaDB | ~50MB |
| FastAPI + Dependencies | ~100MB |
| Python Runtime | ~100MB |
| **Total** | **~400MB** ✅ (fits in 512MB!) |

---

## Configuration for Deployment

Your `config.yaml` is now optimized:

```yaml
embeddings:
  model: "sentence-transformers/paraphrase-MiniLM-L3-v2"  # Lightweight

huggingface:
  use_local_models: false  # Uses API instead (saves RAM)
  use_api: true  # Uses Hugging Face free API
```

---

## Even Lower Memory Option

If you still get memory errors, use the smallest model:

**In `config.yaml`, change:**
```yaml
embeddings:
  model: "sentence-transformers/paraphrase-albert-small-v2"  # Even smaller, <100MB
```

---

## Testing After Deployment

1. Deploy with updated `config.yaml`
2. Check memory usage in Render dashboard
3. Test endpoint:
   ```bash
   curl https://your-url.onrender.com/health
   ```

---

## Trade-offs

**What you gain:**
- ✅ Fits in 512MB RAM
- ✅ Works on Render free tier
- ✅ Still provides good quality analysis

**What you trade:**
- ⚠️ Slightly slower (API calls vs local models)
- ⚠️ Requires internet for Hugging Face API
- ⚠️ Embedding quality slightly lower (but still good)

---

## Alternative: Use Hugging Face API for Everything

If memory is still an issue, you can also use Hugging Face API for embeddings:

1. Get free token: https://huggingface.co/settings/tokens
2. Set in environment: `HUGGINGFACE_API_TOKEN=your_token`
3. The agent will use API for embeddings too (no local model loading)

But the current setup should work fine with the lightweight model!

---

**Your agent is now optimized for 512MB RAM!** 🎉

