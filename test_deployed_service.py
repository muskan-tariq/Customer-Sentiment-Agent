#!/usr/bin/env python3
"""
Test script for deployed Render service
Tests input/output format and validates responses
"""

import requests
import json
import sys
from datetime import datetime

# Your deployed service URL
BASE_URL = "https://customer-sentiment-agent-g5gd.onrender.com"

# Required fields in response (NEW format)
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

# Forbidden fields (OLD format - should NOT be present)
FORBIDDEN_FIELDS = [
    "reasoning",
    "primary_emotion",
    "aspects",
    "summary",
    "comparison"
]


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_health():
    """Test health endpoint"""
    print_section("1. Testing Health Endpoint")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Response:")
            print(json.dumps(data, indent=2))
            print("\n✅ Health check PASSED")
            return True
        else:
            print(f"❌ Health check FAILED: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_analyze_endpoint(payload, test_name):
    """Test analyze endpoint with given payload"""
    print_section(f"2. Testing Analyze Endpoint - {test_name}")
    
    try:
        print("Request Payload:")
        print(json.dumps(payload, indent=2))
        print("\nSending request... (this may take 30-60 seconds)")
        
        response = requests.post(
            f"{BASE_URL}/analyze",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=120  # 2 minutes timeout
        )
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\nResponse:")
            print(json.dumps(data, indent=2))
            
            # Validate schema
            print("\n" + "-" * 70)
            print("Validating Response Schema...")
            print("-" * 70)
            
            errors = []
            
            # Check required fields
            for field in REQUIRED_FIELDS:
                if field not in data:
                    errors.append(f"❌ Missing required field: {field}")
                else:
                    print(f"✅ {field}: {type(data[field]).__name__} = {data[field]}")
            
            # Check forbidden fields (old format)
            for field in FORBIDDEN_FIELDS:
                if field in data:
                    errors.append(f"❌ Forbidden field present (old format): {field}")
            
            # Validate types
            if "sentiment_label" in data and not isinstance(data["sentiment_label"], str):
                errors.append("❌ sentiment_label should be string")
            
            if "sentiment_score" in data and not isinstance(data["sentiment_score"], (int, float)):
                errors.append("❌ sentiment_score should be number")
            
            if "emotion_analysis" in data:
                if not isinstance(data["emotion_analysis"], list):
                    errors.append("❌ emotion_analysis should be array")
                elif len(data["emotion_analysis"]) > 0:
                    # Check emotion structure
                    for emotion in data["emotion_analysis"]:
                        if not isinstance(emotion, dict):
                            errors.append("❌ emotion_analysis items should be objects")
                        elif "emotion" not in emotion or "score" not in emotion:
                            errors.append("❌ emotion_analysis items should have 'emotion' and 'score'")
            
            if "topic_extracted" in data and not isinstance(data["topic_extracted"], list):
                errors.append("❌ topic_extracted should be array")
            
            if "engagement_prediction" in data and not isinstance(data["engagement_prediction"], str):
                errors.append("❌ engagement_prediction should be string")
            
            if "region" in data and data["region"] is not None and not isinstance(data["region"], str):
                errors.append("❌ region should be string or null")
            
            if "recommendation" in data and not isinstance(data["recommendation"], str):
                errors.append("❌ recommendation should be string")
            
            if "database_status" in data and not isinstance(data["database_status"], str):
                errors.append("❌ database_status should be string")
            
            if "langgraph_status" in data and not isinstance(data["langgraph_status"], str):
                errors.append("❌ langgraph_status should be string")
            
            if "timestamp" in data and not isinstance(data["timestamp"], str):
                errors.append("❌ timestamp should be string")
            
            if errors:
                print("\n❌ VALIDATION ERRORS:")
                for error in errors:
                    print(f"  {error}")
                return False
            else:
                print("\n✅ Schema validation PASSED")
                return True
        else:
            print(f"\n❌ Request FAILED: {response.status_code}")
            print(response.text)
            return False
    except requests.exceptions.Timeout:
        print("\n❌ Request TIMED OUT (took longer than 2 minutes)")
        print("This may be normal for first request (cold start)")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("  DEPLOYED SERVICE TEST SUITE")
    print("=" * 70)
    print(f"Service URL: {BASE_URL}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Docs: {BASE_URL}/docs")
    
    results = []
    
    # Test 1: Health check
    results.append(("Health Check", test_health()))
    
    # Test 2: Analyze - Positive sentiment
    results.append(("Analyze (Positive)", test_analyze_endpoint({
        "user": "test_user_001",
        "platform": "twitter",
        "text": "I love this product! It works perfectly and exceeded my expectations. Highly recommend!",
        "country": "Germany",
        "hashtags": ["product", "review"],
        "likes": 150,
        "retweets": 25
    }, "Positive Sentiment")))
    
    # Test 3: Analyze - Negative sentiment
    results.append(("Analyze (Negative)", test_analyze_endpoint({
        "user": "test_user_002",
        "platform": "twitter",
        "text": "Terrible experience. The product broke after one day and customer service was unhelpful. Very disappointed.",
        "country": "USA",
        "hashtags": ["complaint"],
        "likes": 5,
        "retweets": 2
    }, "Negative Sentiment")))
    
    # Test 4: Analyze - Mixed sentiment
    results.append(("Analyze (Mixed)", test_analyze_endpoint({
        "user": "test_user_003",
        "platform": "twitter",
        "text": "Good product quality but customer service needs improvement. Overall satisfied but could be better.",
        "country": "UK"
    }, "Mixed Sentiment")))
    
    # Test 5: Analyze - Minimal input
    results.append(("Analyze (Minimal)", test_analyze_endpoint({
        "text": "This is amazing!",
        "country": "Canada"
    }, "Minimal Input")))
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<50} {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("=" * 70)
    print(f"Total: {len(results)} | Passed: {passed} | Failed: {failed}")
    print("=" * 70)
    
    if failed == 0:
        print("\n🎉 All tests passed! Your deployed service is working correctly!")
        print(f"\n📚 API Documentation: {BASE_URL}/docs")
        print(f"🔗 Health Check: {BASE_URL}/health")
        print(f"🔗 Analyze Endpoint: {BASE_URL}/analyze")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        print("\n💡 Tips:")
        print("   - First request may timeout (cold start) - try again")
        print("   - Check Render logs for errors")
        print("   - Verify timeout settings in Render dashboard")
        return 1


if __name__ == "__main__":
    sys.exit(main())

