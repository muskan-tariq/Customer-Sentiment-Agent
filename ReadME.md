# Quick Start Guide

## Prerequisites

1. Python 3.8 or higher
2. (Optional) Hugging Face API token for faster inference (free tier available)
   - Get one at: https://huggingface.co/settings/tokens
   - If not provided, embeddings will work locally (completely free)

## Installation Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment (Optional)

For faster text generation, create a `.env` file with your Hugging Face token:

```
HUGGINGFACE_API_TOKEN=your_huggingface_token_here
```

Or set it as an environment variable:

**Windows (PowerShell):**
```powershell
$env:HUGGINGFACE_API_TOKEN="your_huggingface_token_here"
```

**Linux/Mac:**
```bash
export HUGGINGFACE_API_TOKEN="your_huggingface_token_here"
```

**Note:** If you don't provide a token, the agent will use local models (slower but completely free). Embeddings always work locally without any API key.

### 3. Run the Server

```bash
python main.py
```

The server will start on `http://localhost:8000`

### 4. Test the API

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Analyze Text:**
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"text": "I love this product! It works perfectly."}'
```

### 5. Run Tests

```bash
pytest tests/ -v
```

## Example Python Client

```python
import requests

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())

# Analyze text
response = requests.post(
    "http://localhost:8000/analyze",
    json={"text": "The service was excellent, but the price is too high."}
)
print(response.json())
```

## Troubleshooting

### Hugging Face API Token Error
- The agent works without an API token (uses local models)
- For faster inference, get a free token from https://huggingface.co/settings/tokens
- Embeddings work locally without any API key

### Port Already in Use
- Change the port in `config.yaml` (default: 8000)
- Or stop the process using port 8000

### Import Errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.8+)

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Customize `config.yaml` for your needs
- Check logs in `./logs/agent.log` for debugging

