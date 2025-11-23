# CRITICAL: PyTorch CUDA Libraries Causing Memory Overflow

## Problem
PyTorch is downloading **~3GB of CUDA libraries** (nvidia-* packages) which exceeds Render's 512MB limit.

## Root Cause
- `torch>=2.0.0` downloads full CUDA version by default
- CUDA libraries: ~900MB torch + ~2GB nvidia packages = **~3GB total**
- Render free tier: **512MB limit**

## Solution Applied

### 1. Created CPU-Only Requirements File ✅
- `requirements-deploy.txt` - Uses CPU-only PyTorch
- Saves ~2GB by excluding CUDA libraries

### 2. Updated Render Config ✅
- `render.yaml` - Uses `requirements-deploy.txt` for build
- Falls back to CPU-only install if needed

---

## Next Steps

### Option 1: Use Deployment Requirements (Recommended)

**Update Render Build Command:**
```
pip install -r requirements-deploy.txt
```

This installs CPU-only PyTorch (no CUDA).

### Option 2: Manual CPU-Only Install

**Update Render Build Command:**
```
pip install --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt
```

This forces CPU-only PyTorch installation.

---

## Memory Comparison

| Component | With CUDA | CPU-Only | Savings |
|-----------|-----------|----------|---------|
| PyTorch | ~900MB | ~200MB | ~700MB |
| CUDA Libraries | ~2GB | 0MB | ~2GB |
| **Total** | **~3GB** | **~200MB** | **~2.8GB** |

**CPU-only saves ~2.8GB!**

---

## Updated Render Settings

**Build Command:**
```
pip install -r requirements-deploy.txt
```

**Or:**
```
pip install --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt
```

---

## Why This Works

- Your agent uses `use_local_models: false` (API mode)
- Sentence-transformers only needs CPU PyTorch
- No GPU/CUDA needed for deployment
- CPU-only PyTorch is sufficient

---

## After Fix

Expected memory usage:
- CPU-only PyTorch: ~200MB
- Embedding model: ~100MB
- ChromaDB: ~50MB
- FastAPI + Dependencies: ~100MB
- Python Runtime: ~50MB
- **Total: ~500MB** ✅ (fits in 512MB!)

---

**Update Render build command and redeploy!** 🚀

