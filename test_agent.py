"""
Simple test script to verify the agent is working
Run this after starting the server with: python main.py
"""

import requests
import json
import time

# Agent URL
AGENT_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint"""
    print("=" * 60)
    print("TEST 1: Health Check")
    print("=" * 60)
    try:
        response = requests.get(f"{AGENT_URL}/health", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        assert response.status_code == 200, "Health check failed"
        print("Health check PASSED\n")
        return True
    except Exception as e:
        print(f"❌ Health check FAILED: {e}\n")
        return False

def test_analyze():
    """Test analyze endpoint with new format"""
    print("=" * 60)
    print("TEST 2: Analyze Endpoint (New Format)")
    print("=" * 60)
    try:
        # Test with new structured format
        payload = {
            "user": "user_1234",
            "platform": "twitter",
            "timestamp": "2025-10-21T13:45:00Z",
            "text": "I love this product! It's amazing and works perfectly.",
            "hashtags": ["TechTrends"],
            "likes": 542,
            "retweets": 120,
            "country": "Germany"
        }
        
        print(f"Sending request with structured data:")
        print(f"  - User: {payload['user']}")
        print(f"  - Platform: {payload['platform']}")
        print(f"  - Text: {payload['text'][:50]}...")
        
        response = requests.post(
            f"{AGENT_URL}/analyze",
            json=payload,
            timeout=60
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nResponse Structure (NEW Format):")
            print(f"  - Sentiment Label: {result.get('sentiment_label')}")
            print(f"  - Sentiment Score: {result.get('sentiment_score')}")
            print(f"  - Emotions: {len(result.get('emotion_analysis', []))} emotions detected")
            print(f"  - Engagement: {result.get('engagement_prediction')}")
            print(f"  - Topics: {result.get('topic_extracted', [])}")
            print(f"  - Region: {result.get('region')}")
            print(f"  - Recommendation: {result.get('recommendation', '')[:60]}...")
            
            # Validate NEW format structure - ENFORCE strict schema
            required_fields = [
                "sentiment_label",
                "sentiment_score",
                "emotion_analysis",
                "engagement_prediction",
                "topic_extracted",
                "recommendation",
                "region",
                "database_status",
                "langgraph_status",
                "timestamp",
            ]
            missing = [f for f in required_fields if f not in result]
            
            # Check for OLD fields that should NOT exist
            old_fields = ["sentiment", "summary", "aspects", "comparison", "confidence", 
                         "status", "agent", "input", "result", "memory_used", 
                         "response_type", "session_id", "confidence_level"]
            found_old_fields = [f for f in old_fields if f in result]
            
            if missing:
                print(f"  ❌ MISSING REQUIRED FIELDS: {missing}")
                return False
            elif found_old_fields:
                print(f"  ❌ OLD FIELDS FOUND (should be removed): {found_old_fields}")
                return False
            else:
                print("  All required NEW fields present")
                print("  No old fields found")
                
                # Validate emotion_analysis structure
                emotion_analysis = result.get("emotion_analysis", [])
                if not isinstance(emotion_analysis, list):
                    print(f"  ❌ emotion_analysis must be an array, got: {type(emotion_analysis)}")
                    return False
                for emo in emotion_analysis:
                    if not isinstance(emo, dict) or "emotion" not in emo or "score" not in emo:
                        print(f"  ❌ Invalid emotion_analysis format: {emo}")
                        return False
                
                print("  emotion_analysis format is correct")
            
            print(f"\nFull Response (first 600 chars):")
            print(json.dumps(result, indent=2)[:600] + "...")
            print("\nAnalyze endpoint PASSED\n")
            return True
        else:
            print(f"❌ Analyze endpoint FAILED: {response.text}\n")
            return False
            
    except Exception as e:
        print(f"❌ Analyze endpoint FAILED: {e}\n")
        return False

def test_supervisor_request():
    """Test request format that supervisor agent would use"""
    print("=" * 60)
    print("TEST 3: Supervisor Agent Request Format")
    print("=" * 60)
    try:
        # Simulate supervisor agent request (new format)
        supervisor_payload = {
            "request_type": "customer_query",
            "customer_id": "CUST_12345",
            "session_id": "SESSION_XYZ_001",
            "query": {
                "text": "The customer service was terrible, but the product quality is excellent.",
                "timestamp": "2025-10-22T08:45:00Z",
                "channel": "web_chat"
            },
            "context": {
                "previous_interactions": 3,
                "language": "en"
            },
            "meta": {
                "priority": "normal",
                "requested_at": "2025-10-22T08:45:02Z"
            }
        }
        
        print("Simulating supervisor agent request...")
        print(f"Payload structure: request_type={supervisor_payload['request_type']}")
        print(f"  - Customer ID: {supervisor_payload['customer_id']}")
        print(f"  - Session ID: {supervisor_payload['session_id']}")
        print(f"  - Text: {supervisor_payload['query']['text'][:50]}...")
        
        response = requests.post(
            f"{AGENT_URL}/analyze",
            json=supervisor_payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nSupervisor request successful!")
            print(f"Sentiment Label: {result.get('sentiment_label')}")
            print(f"Sentiment Score: {result.get('sentiment_score')}")
            print(f"Engagement: {result.get('engagement_prediction')}")
            print(f"Topics: {result.get('topic_extracted', [])}")
            print(f"Region: {result.get('region')}")
            print(f"Recommendation: {result.get('recommendation', '')[:60]}...")
            print(f"Database Status: {result.get('database_status')}")
            print(f"LangGraph Status: {result.get('langgraph_status')}")
            print(f"Timestamp: {result.get('timestamp')}")
            
            # Validate NEW format - enforce schema
            required_fields = [
                "sentiment_label",
                "sentiment_score",
                "emotion_analysis",
                "engagement_prediction",
                "topic_extracted",
                "recommendation",
                "region",
                "database_status",
                "langgraph_status",
                "timestamp",
            ]
            missing = [f for f in required_fields if f not in result]
            old_fields = ["sentiment", "summary", "aspects", "comparison", "confidence", 
                         "status", "agent", "input", "result", "memory_used"]
            found_old = [f for f in old_fields if f in result]
            
            if missing:
                print(f"  ❌ MISSING FIELDS: {missing}")
                return False
            if found_old:
                print(f"  ❌ OLD FIELDS FOUND: {found_old}")
                return False
            
            print("\nSupervisor request format PASSED (NEW format validated)\n")
            return True
        else:
            print(f"❌ Supervisor request FAILED: {response.text}\n")
            return False
            
    except Exception as e:
        print(f"❌ Supervisor request FAILED: {e}\n")
        return False

def test_multiple_requests():
    """Test multiple requests to check memory functionality"""
    print("=" * 60)
    print("TEST 4: Multiple Requests (Memory Test)")
    print("=" * 60)
    try:
        payload1 = {
            "user": "user_test",
            "platform": "twitter",
            "text": "This is a great product!",
            "country": "USA"
        }
        payload2 = {
            "user": "user_test",
            "platform": "twitter",
            "text": "This is a great product!",  # Same text - should use memory
            "country": "USA"
        }
        
        print(f"Request 1: '{payload1['text']}'")
        response1 = requests.post(f"{AGENT_URL}/analyze", json=payload1, timeout=60)
        result1 = response1.json()
        sentiment1 = result1.get('sentiment_label', 'N/A')
        score1 = result1.get('sentiment_score', 0)
        print(f"  Sentiment: {sentiment1} (score: {score1})")
        
        # Validate NEW format
        required = [
            "sentiment_label",
            "sentiment_score",
            "emotion_analysis",
            "engagement_prediction",
            "topic_extracted",
            "recommendation",
            "region",
            "database_status",
            "langgraph_status",
            "timestamp",
        ]
        if not all(f in result1 for f in required):
            print(f"  ❌ Request 1 missing required fields")
            return False
        
        time.sleep(1)  # Small delay
        
        print(f"\nRequest 2: '{payload2['text']}' (same text)")
        response2 = requests.post(f"{AGENT_URL}/analyze", json=payload2, timeout=60)
        result2 = response2.json()
        sentiment2 = result2.get('sentiment_label', 'N/A')
        score2 = result2.get('sentiment_score', 0)
        print(f"  Sentiment: {sentiment2} (score: {score2})")
        
        # Validate NEW format
        if not all(f in result2 for f in required):
            print(f"  ❌ Request 2 missing required fields")
            return False
        
        # Check if results are similar (memory might be used)
        if abs(score1 - score2) < 0.1 and sentiment1 == sentiment2:
            print("\nResults are consistent (memory may have been used)")
        else:
            print("\n⚠️  Results differ (memory not reused or threshold not met)")
        
        print("\nMultiple requests test PASSED\n")
        return True
        
    except Exception as e:
        print(f"❌ Multiple requests test FAILED: {e}\n")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("SENTIMENT ANALYSIS AGENT - TESTING SUITE")
    print("=" * 60)
    print(f"\nTesting agent at: {AGENT_URL}")
    print("Make sure the server is running: python main.py\n")
    
    results = []
    results.append(("Health Check", test_health()))
    results.append(("Analyze Endpoint", test_analyze()))
    results.append(("Supervisor Request", test_supervisor_request()))
    results.append(("Memory System", test_multiple_requests()))
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Agent is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test suite error: {e}")

