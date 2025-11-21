"""
Strict schema validation test for NEW format
This test will FAIL if any old fields are present or new fields are missing
"""

import requests
import json

AGENT_URL = "http://localhost:8000"

def test_new_format_schema():
    """Test that response matches NEW format exactly"""
    print("=" * 60)
    print("SCHEMA VALIDATION TEST - NEW FORMAT")
    print("=" * 60)
    
    # Test input
    payload = {
        "user": "user_1234",
        "platform": "twitter",
        "timestamp": "2025-10-21T13:45:00Z",
        "text": "The new product launch blew my mind! So innovative 🔥 #TechTrends",
        "hashtags": ["TechTrends"],
        "likes": 542,
        "retweets": 120,
        "country": "Germany"
    }
    
    print(f"\nSending request with structured data...")
    response = requests.post(f"{AGENT_URL}/analyze", json=payload, timeout=60)
    
    if response.status_code != 200:
        print(f"❌ Request failed: {response.status_code}")
        print(response.text)
        return False
    
    result = response.json()
    
    # REQUIRED NEW FIELDS (must be present in agent response)
    required_fields = {
        "sentiment_label": str,
        "sentiment_score": (int, float),
        "emotion_analysis": list,
        "engagement_prediction": str,
        "topic_extracted": list,
        "recommendation": str,
        "region": (str, type(None)),  # Can be None
        "database_status": str,
        "langgraph_status": str,
        "timestamp": str,
    }
    
    # FORBIDDEN OLD FIELDS (must NOT be present)
    forbidden_fields = [
        "sentiment", "summary", "aspects", "comparison", "confidence",
        "status", "agent", "input", "result", "memory_used",
        "response_type", "session_id", "confidence_level"
    ]
    
    print("\n" + "=" * 60)
    print("VALIDATING NEW FORMAT SCHEMA")
    print("=" * 60)
    
    # Check required fields
    print("\nChecking REQUIRED fields:")
    missing = []
    wrong_type = []
    for field, expected_type in required_fields.items():
        if field not in result:
            missing.append(field)
            print(f"  ❌ MISSING: {field}")
        else:
            value = result[field]
            if isinstance(expected_type, tuple):
                if not isinstance(value, expected_type):
                    wrong_type.append(f"{field} (expected {expected_type}, got {type(value)})")
                    print(f"  ❌ WRONG TYPE: {field} (expected {expected_type}, got {type(value)})")
                else:
                    print(f"  OK {field}: {type(value).__name__}")
            else:
                if not isinstance(value, expected_type):
                    wrong_type.append(f"{field} (expected {expected_type.__name__}, got {type(value).__name__})")
                    print(f"  ❌ WRONG TYPE: {field} (expected {expected_type.__name__}, got {type(value).__name__})")
                else:
                    print(f"  OK {field}: {type(value).__name__}")
    
    # Check forbidden fields
    print("\nChecking FORBIDDEN (old) fields:")
    found_forbidden = []
    for field in forbidden_fields:
        if field in result:
            found_forbidden.append(field)
            print(f"  ❌ FORBIDDEN FIELD FOUND: {field} = {result[field]}")
        else:
            print(f"  OK {field}: not present")
    
    # Validate emotion_analysis structure
    print("\nValidating emotion_analysis structure:")
    emotion_analysis = result.get("emotion_analysis", [])
    if not isinstance(emotion_analysis, list):
        print(f"  ❌ emotion_analysis must be a list, got {type(emotion_analysis)}")
        return False
    
    if len(emotion_analysis) == 0:
        print(f"  ⚠️  emotion_analysis is empty")
    else:
        for i, emo in enumerate(emotion_analysis):
            if not isinstance(emo, dict):
                print(f"  ❌ emotion_analysis[{i}] must be a dict, got {type(emo)}")
                return False
            if "emotion" not in emo:
                print(f"  ❌ emotion_analysis[{i}] missing 'emotion' field")
                return False
            if "score" not in emo:
                print(f"  ❌ emotion_analysis[{i}] missing 'score' field")
                return False
            if not isinstance(emo["emotion"], str):
                print(f"  ❌ emotion_analysis[{i}]['emotion'] must be string")
                return False
            if not isinstance(emo["score"], (int, float)):
                print(f"  ❌ emotion_analysis[{i}]['score'] must be number")
                return False
        print(f"  OK emotion_analysis: {len(emotion_analysis)} emotions, all valid")
    
    # Validate topic_extracted structure
    print("\nValidating topic_extracted structure:")
    topics = result.get("topic_extracted", [])
    if not isinstance(topics, list):
        print(f"  ❌ topic_extracted must be a list, got {type(topics)}")
        return False
    for topic in topics:
        if not isinstance(topic, str):
            print(f"  ❌ topic_extracted contains non-string: {topic}")
            return False
    print(f"  OK topic_extracted: {len(topics)} topics, all valid")
    
    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    if missing:
        print(f"❌ MISSING REQUIRED FIELDS: {missing}")
        return False
    
    if wrong_type:
        print(f"❌ WRONG FIELD TYPES: {wrong_type}")
        return False
    
    if found_forbidden:
        print(f"❌ FORBIDDEN OLD FIELDS FOUND: {found_forbidden}")
        return False
    
    print("\nALL VALIDATIONS PASSED!")
    print("\nResponse matches NEW format exactly:")
    print(json.dumps(result, indent=2))
    
    return True

if __name__ == "__main__":
    try:
        success = test_new_format_schema()
        if success:
            print("\n🎉 Schema validation PASSED - Agent uses NEW format correctly!")
        else:
            print("\n❌ Schema validation FAILED - Agent needs to be updated!")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()

