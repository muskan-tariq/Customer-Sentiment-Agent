"""
Main entry point for Sentiment Analysis Agent
"""

import uvicorn
from agent.utils.config_loader import load_config
from agent.utils.logger import setup_logging
from agent.utils.mongodb_logger import MongoLogger
from agent.memory.vector_store import VectorStore
from agent.analysis.analysis_engine import AnalysisEngine
from agent.workflow.agent_workflow import AgentWorkflow
from agent.api.api_server import create_app


def main():
    """Initialize and run the agent"""
    # Load configuration
    config = load_config()
    
    # Setup logging
    setup_logging(config)
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Starting Sentiment Analysis Agent...")
    
    # Initialize components
    logger.info("Initializing vector store...")
    memory_store = VectorStore(config)
    
    logger.info("Initializing analysis engine...")
    analysis_engine = AnalysisEngine(config)
    
    logger.info("Initializing LangGraph workflow...")
    workflow = AgentWorkflow(memory_store, analysis_engine)
    
    # Initialize MongoDB logger
    logger.info("Initializing MongoDB logger...")
    mongodb_logger = MongoLogger(config)
    
    # Create FastAPI app
    logger.info("Creating FastAPI application...")
    app = create_app(workflow, config, mongodb_logger)
    
    # Get API configuration
    api_config = config.get("api", {})
    host = api_config.get("host", "0.0.0.0")
    
    # Get port from environment (for Replit/cloud platforms) or config
    import os
    port = int(os.getenv("PORT", api_config.get("port", 8000)))
    
    logger.info(f"Starting server on {host}:{port}")
    
    # Run server
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=api_config.get("log_level", "info").lower()
    )


if __name__ == "__main__":
    main()

