"""
Example: How a Supervisor Agent would call this Sentiment Agent
This demonstrates the request/response format for agent-to-agent communication
"""

import requests
import json
from typing import Dict, Any, Optional

class SupervisorAgent:
    """
    Example supervisor agent that calls the sentiment analysis agent
    """
    
    def __init__(self, sentiment_agent_url: str = "http://localhost:8000"):
        self.sentiment_agent_url = sentiment_agent_url
    
    def check_agent_health(self) -> bool:
        """Check if sentiment agent is available"""
        try:
            response = requests.get(f"{self.sentiment_agent_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def analyze_sentiment(self, text: str, structured_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Send text to sentiment agent for analysis (new format)
        
        Args:
            text: Text to analyze
            structured_data: Optional structured data (user, platform, country, etc.)
            
        Returns:
            Analysis result from sentiment agent in new format
        """
        try:
            # Prepare request in new format
            if structured_data:
                payload = structured_data.copy()
                if "text" not in payload:
                    payload["text"] = text
            else:
                # Default structured format
                payload = {
                    "user": "supervisor_user",
                    "platform": "internal",
                    "text": text,
                    "timestamp": "2025-10-22T08:45:00Z",
                    "country": "Unknown"
                }
            
            # Send POST request to sentiment agent
            response = requests.post(
                f"{self.sentiment_agent_url}/analyze",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "status": "error",
                    "error": f"Agent returned status {response.status_code}",
                    "detail": response.text
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def process_feedback(self, feedback_text: str, structured_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Example: Supervisor processes customer feedback using sentiment agent (new format)
        
        Args:
            feedback_text: Customer feedback text
            structured_data: Optional structured data
            
        Returns:
            Processed result with sentiment analysis in new format
        """
        print(f"Supervisor: Processing feedback...")
        print(f"Text: {feedback_text[:100]}...")
        
        # Check agent health first
        if not self.check_agent_health():
            return {
                "status": "error",
                "error": "Sentiment agent is not available"
            }
        
        # Prepare structured data if not provided
        if not structured_data:
            structured_data = {
                "user": "customer_feedback",
                "platform": "web",
                "text": feedback_text,
                "timestamp": "2025-10-22T08:45:00Z"
            }
        
        # Get analysis from sentiment agent
        analysis = self.analyze_sentiment(feedback_text, structured_data)
        
        if analysis.get("status") == "success" or "sentiment_label" in analysis:
            print(f"\nSupervisor: Received analysis from sentiment agent (New Format):")
            print(f"  - Response Type: {analysis.get('response_type', 'N/A')}")
            print(f"  - Sentiment Label: {analysis.get('sentiment_label', 'N/A')}")
            print(f"  - Sentiment Score: {analysis.get('sentiment_score', 0):.2f}")
            print(f"  - Engagement: {analysis.get('engagement_prediction', 'N/A')}")
            print(f"  - Topics: {analysis.get('topic_extracted', [])}")
            print(f"  - Region: {analysis.get('region', 'N/A')}")
            print(f"  - Memory Used: {analysis.get('memory_used', False)}")
            print(f"  - Recommendation: {analysis.get('recommendation', 'N/A')[:80]}...")
            
            return analysis
        else:
            print(f"Supervisor: Error from sentiment agent: {analysis.get('error')}")
            return analysis


def main():
    """Example usage"""
    print("=" * 60)
    print("SUPERVISOR AGENT EXAMPLE")
    print("=" * 60)
    print("\nThis demonstrates how a supervisor agent would call")
    print("the sentiment analysis agent.\n")
    
    # Initialize supervisor
    supervisor = SupervisorAgent()
    
    # Check if sentiment agent is running
    print("Checking sentiment agent health...")
    if not supervisor.check_agent_health():
        print("Sentiment agent is not running!")
        print("Please start it with: python main.py")
        return
    
    print("Sentiment agent is healthy\n")
    
    # Example 1: Analyze positive feedback (new structured format)
    print("Example 1: Positive Feedback (Structured Format)")
    print("-" * 60)
    feedback1_data = {
        "user": "user_1234",
        "platform": "twitter",
        "timestamp": "2025-10-21T13:45:00Z",
        "text": "I love this product! It's amazing and works perfectly. Highly recommend! 🔥 #TechTrends",
        "hashtags": ["TechTrends"],
        "likes": 542,
        "retweets": 120,
        "country": "Germany"
    }
    result1 = supervisor.process_feedback(feedback1_data["text"], feedback1_data)
    print(f"\nFull result: {json.dumps(result1, indent=2)[:400]}...\n")
    
    # Example 2: Analyze negative feedback
    print("Example 2: Negative Feedback")
    print("-" * 60)
    feedback2_data = {
        "user": "user_5678",
        "platform": "web",
        "text": "Terrible service. The product broke after one day. Very disappointed.",
        "country": "USA"
    }
    result2 = supervisor.process_feedback(feedback2_data["text"], feedback2_data)
    print(f"\nFull result: {json.dumps(result2, indent=2)[:400]}...\n")
    
    # Example 3: Supervisor request format
    print("Example 3: Supervisor Request Format")
    print("-" * 60)
    feedback3_data = {
        "request_type": "customer_query",
        "customer_id": "CUST_12345",
        "session_id": "SESSION_XYZ_001",
        "query": {
            "text": "The product quality is excellent, but customer service needs improvement.",
            "timestamp": "2025-10-22T08:45:00Z",
            "channel": "web_chat"
        },
        "context": {
            "previous_interactions": 3,
            "language": "en"
        }
    }
    result3 = supervisor.process_feedback(feedback3_data["query"]["text"], feedback3_data)
    print(f"\nFull result: {json.dumps(result3, indent=2)[:400]}...\n")
    
    print("=" * 60)
    print("Supervisor agent example completed!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n\nError: {e}")

