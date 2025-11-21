# Quick Start Guide

## Prerequisites

1. Python 3.8 or higher


## Installation Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment (Optional)

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


