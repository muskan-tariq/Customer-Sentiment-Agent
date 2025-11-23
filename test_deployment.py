#!/usr/bin/env python3
"""
Test script for Render deployment
Tests all endpoints and validates responses
"""

import requests
import json
import sys
from datetime import datetime

# Your Render URL
BASE_URL = "https://customer-sentiment-agent-g5gd.onrender.com"

# Required fields in response
REQUIRED_FIELDS = [
    "sentiment_label",
    "sentiment_score",
    "emotion_analysis",
    "engagement_prediction",
    "topic_extracted",
    "region",
    "recommendation",
    "database_status",
    "langgraph_status",
    "timestamp"
]


def test_health():
    """Test health endpoint"""
    print("=" * 60)
    print("Testing Health Endpoint...")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Response:")
            print(json.dumps(data, indent=2))
            print("\n✅ Health check passed!")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_root():
    """Test root endpoint"""
    print("\n" + "=" * 60)
    print("Testing Root Endpoint...")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Response:")
            print(json.dumps(data, indent=2))
            print("\n✅ Root endpoint passed!")
            return True
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_analyze(payload):
    """Test analyze endpoint"""
    print("\n" + "=" * 60)
    print("Testing Analyze Endpoint...")
    print("=" * 60)
    
    try:
        print("Request Payload:")
        print(json.dumps(payload, indent=2))
        
        response = requests.post(
            f"{BASE_URL}/analyze",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=120  # Increased timeout for cold start (model loading)
        )
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\nResponse:")
            print(json.dumps(data, indent=2))
            
            # Validate required fields
            print("\n" + "=" * 60)
            print("Validating Response Schema...")
            print("=" * 60)
            
            missing_fields = []
            for field in REQUIRED_FIELDS:
                if field not in data:
                    missing_fields.append(field)
                else:
                    print(f"✅ {field}: {type(data[field]).__name__}")
            
            if missing_fields:
                print(f"\n❌ Missing fields: {missing_fields}")
                return False
            else:
                print("\n✅ All required fields present!")
                
            # Validate types
            if not isinstance(data["sentiment_label"], str):
                print("❌ sentiment_label should be string")
                return False
            if not isinstance(data["sentiment_score"], (int, float)):
                print("❌ sentiment_score should be number")
                return False
            if not isinstance(data["emotion_analysis"], list):
                print("❌ emotion_analysis should be array")
                return False
            if not isinstance(data["topic_extracted"], list):
                print("❌ topic_extracted should be array")
                return False
                
            print("\n✅ Schema validation passed!")
            return True
        else:
            print(f"❌ Analyze endpoint failed: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("DEPLOYMENT TEST SUITE")
    print("=" * 60)
    print(f"Testing: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    results = []
    
    # Test 1: Health check
    results.append(("Health Check", test_health()))
    
    # Test 2: Root endpoint
    results.append(("Root Endpoint", test_root()))
    
    # Test 3: Analyze endpoint - Positive
    results.append(("Analyze (Positive)", test_analyze({
        "user": "test_user",
        "platform": "twitter",
        "text": "I love this product! It works perfectly and exceeded my expectations.",
        "country": "Germany"
    })))
    
    # Test 4: Analyze endpoint - Negative
    results.append(("Analyze (Negative)", test_analyze({
        "user": "test_user_2",
        "platform": "twitter",
        "text": "Terrible experience. The product broke after one day and customer service was unhelpful.",
        "country": "USA"
    })))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("=" * 60)
    print(f"Total: {len(results)} | Passed: {passed} | Failed: {failed}")
    print("=" * 60)
    
    if failed == 0:
        print("\n🎉 All tests passed! Your deployment is working correctly!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

