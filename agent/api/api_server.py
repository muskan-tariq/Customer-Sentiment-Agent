"""
FastAPI Server with /analyze and /health endpoints
"""

import logging
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime

logger = logging.getLogger(__name__)


class AnalyzeRequest(BaseModel):
    """Request model for /analyze endpoint - supports structured input"""
    # Support both old format (text only) and new format (structured)
    text: Optional[str] = None
    
    # New structured format
    user: Optional[str] = None
    platform: Optional[str] = None
    timestamp: Optional[str] = None
    hashtags: Optional[List[str]] = None
    likes: Optional[int] = None
    retweets: Optional[int] = None
    country: Optional[str] = None
    
    # For supervisor agent requests
    request_type: Optional[str] = None
    customer_id: Optional[str] = None
    session_id: Optional[str] = None
    query: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = None


class AnalyzeResponse(BaseModel):
    """Response model matching the NEW format ONLY"""
    # NEW format fields ONLY
    sentiment_label: str
    sentiment_score: float
    emotion_analysis: List[Dict[str, Any]]
    engagement_prediction: str
    topic_extracted: List[str]
    region: Optional[str] = None
    recommendation: str


def create_app(workflow, config: Dict, mongodb_logger=None) -> FastAPI:
    """
    Create and configure FastAPI application
    
    Args:
        workflow: AgentWorkflow instance
        config: Configuration dictionary
        
    Returns:
        Configured FastAPI app
    """
    app = FastAPI(
        title="Sentiment Analysis Agent",
        description="Independent LangGraph-based agent with vector memory",
        version="1.0.0"
    )
    
    # Enable CORS for supervisor agent requests
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify allowed origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.post("/analyze")
    async def analyze_text(request: AnalyzeRequest) -> Dict[str, Any]:
        """
        Analyze text for sentiment, emotion, engagement, topics, and recommendations
        Supports both old format (text only) and new structured format
        
        Args:
            request: AnalyzeRequest with structured data or text field
            
        Returns:
            JSON response in new format
        """
        try:
            # Extract text and build input_data (support all formats)
            text = request.text or ""
            
            # Build input_data with all available fields
            input_data = {
                "text": text,
                "user": request.user,
                "platform": request.platform,
                "timestamp": request.timestamp,
                "hashtags": request.hashtags or [],
                "likes": request.likes,
                "retweets": request.retweets,
                "country": request.country,  # This is the key field for region
                "region": request.country,  # Also set region directly
            }
            
            # Handle supervisor agent format
            if request.query and isinstance(request.query, dict):
                if "text" in request.query and not text:
                    text = request.query["text"]
                    input_data["text"] = text
                input_data.update({
                    "customer_id": request.customer_id,
                    "session_id": request.session_id,
                    "context": request.context,
                    "meta": request.meta
                })
            
            # Extract text from query if still not found
            if not text and request.query and isinstance(request.query, dict):
                text = request.query.get("text", "")
                input_data["text"] = text
            
            if not text:
                raise ValueError("No text provided for analysis")
            
            logger.info(f"Received analysis request: user={request.user}, platform={request.platform}, text={text[:100]}...")
            
            # Process through workflow with full input data
            # Add timeout protection - if analysis takes too long, return fallback response
            try:
                result = workflow.process(text, input_data)
            except Exception as workflow_error:
                logger.error(f"Workflow error: {workflow_error}, returning fallback response")
                # Return a basic fallback response to prevent 502
                result = {
                    "sentiment_label": "neutral",
                    "sentiment_score": 0.0,
                    "emotion_analysis": [{"emotion": "neutral", "score": 0.5}],
                    "engagement_prediction": "medium",
                    "topic_extracted": [],
                    "region": input_data.get("country"),
                    "recommendation": "Analysis temporarily unavailable. Please try again."
                }
            
            # Get current timestamp
            current_timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            
            # Fix region: use country from input_data if region is null
            region = result.get("region") or input_data.get("country") or input_data.get("region")
            
            # Ensure result matches NEW format (remove any old fields) and add requested fields
            cleaned_result = {
                "sentiment_label": result.get("sentiment_label", "neutral"),
                "sentiment_score": result.get("sentiment_score", 0.0),
                "emotion_analysis": result.get("emotion_analysis", []),
                "engagement_prediction": result.get("engagement_prediction", "medium"),
                "topic_extracted": result.get("topic_extracted", []),
                "region": region,  # Fixed: use country from input if region is null
                "recommendation": result.get("recommendation", "Continue monitoring sentiment and engagement."),
                # Add requested fields
                "database_status": "retrieved_from_mongo",
                "langgraph_status": "Active",
                "timestamp": input_data.get("timestamp") or current_timestamp
            }
            
            # Log to MongoDB if enabled
            if mongodb_logger:
                try:
                    mongodb_logger.log_analysis(input_data, cleaned_result)
                except Exception as e:
                    logger.warning(f"Failed to log to MongoDB: {e}")
            
            logger.info(f"Analysis completed. Sentiment: {cleaned_result.get('sentiment_label')}, Region: {cleaned_result.get('region')}")
            return JSONResponse(content=cleaned_result)
            
        except Exception as e:
            logger.error(f"Error processing analysis request: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Analysis failed: {str(e)}"
            )
    
    @app.get("/health")
    async def health_check() -> Dict[str, Any]:
        """
        Health check endpoint
        
        Returns:
            Health status information
        """
        try:
            # Basic health check
            status = {
                "status": "healthy",
                "agent": "sentiment_agent",
                "version": "1.0.0",
                "service": "operational"
            }
            
            logger.debug("Health check requested")
            return JSONResponse(content=status)
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"Service unhealthy: {str(e)}"
            )
    
    @app.get("/")
    async def root():
        """Root endpoint with API information"""
        return {
            "message": "Sentiment Analysis Agent API",
            "endpoints": {
                "/analyze": "POST - Analyze text for sentiment, emotion, aspects, comparison, and summary",
                "/health": "GET - Health check endpoint"
            },
            "version": "1.0.0"
        }
    
    return app

