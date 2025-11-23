"""
WSGI entry point for Gunicorn (Render deployment)
"""

import os
from agent.utils.config_loader import load_config
from agent.utils.logger import setup_logging
from agent.utils.mongodb_logger import MongoLogger
from agent.memory.vector_store import VectorStore
from agent.analysis.analysis_engine import AnalysisEngine
from agent.workflow.agent_workflow import AgentWorkflow
from agent.api.api_server import create_app

# Load configuration
config = load_config()

# Setup logging
setup_logging(config)
import logging
logger = logging.getLogger(__name__)
logger.info("Initializing Sentiment Analysis Agent for deployment...")

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

logger.info("Agent initialized and ready to serve requests!")

