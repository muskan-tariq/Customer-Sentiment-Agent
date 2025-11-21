"""
MongoDB logging utility for storing analysis results
"""

import os
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import pymongo
try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False
    logger.warning("pymongo not available - MongoDB logging disabled")


class MongoLogger:
    """MongoDB logger for storing analysis results"""

    def __init__(self, config: Dict):
        """
        Initialize MongoDB logger

        Args:
            config: Configuration dictionary with mongodb settings
        """
        self.config = config
        self.client = None
        self.db = None
        self.collection = None
        self.enabled = config.get("mongodb", {}).get("enabled", False)

        if not PYMONGO_AVAILABLE:
            logger.warning("pymongo not installed - MongoDB logging disabled")
            self.enabled = False
            return

        if not self.enabled:
            logger.info("MongoDB logging disabled in config")
            return

        try:
            mongodb_config = config.get("mongodb", {})

            # Connection string precedence:
            # 1. Environment variable MONGODB_URI
            # 2. connection_string from config.yaml
            # 3. Default localhost
            env_uri = os.getenv("MONGODB_URI")
            if env_uri:
                connection_string = env_uri
            else:
                connection_string = mongodb_config.get("connection_string") or "mongodb://localhost:27017/"

            database_name = mongodb_config.get("database", "sentiment_agent")
            collection_name = mongodb_config.get("collection", "analysis_logs")

            # Connect to MongoDB
            self.client = MongoClient(
                connection_string,
                serverSelectionTimeoutMS=5000,
            )

            # Test connection
            self.client.admin.command("ping")

            self.db = self.client[database_name]
            self.collection = self.db[collection_name]

            logger.info(f"MongoDB logger initialized: {database_name}.{collection_name}")

        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.warning(f"MongoDB connection failed: {e} - Logging to MongoDB disabled")
            self.enabled = False
            self.client = None
        except Exception as e:
            logger.error(f"Error initializing MongoDB logger: {e}")
            self.enabled = False
            self.client = None

    def log_analysis(self, input_data: Dict[str, Any], result: Dict[str, Any]) -> bool:
        """
        Log analysis result to MongoDB

        Args:
            input_data: Input data from request
            result: Analysis result

        Returns:
            True if logged successfully, False otherwise
        """
        if not self.enabled or not self.collection:
            return False

        try:
            log_entry = {
                "timestamp": datetime.utcnow(),
                "input": {
                    "user": input_data.get("user"),
                    "platform": input_data.get("platform"),
                    "text": (input_data.get("text") or "")[:500],
                    "country": input_data.get("country"),
                    "hashtags": input_data.get("hashtags", []),
                    "likes": input_data.get("likes"),
                    "retweets": input_data.get("retweets"),
                    "session_id": input_data.get("session_id"),
                    "customer_id": input_data.get("customer_id"),
                },
                "output": {
                    "sentiment_label": result.get("sentiment_label"),
                    "sentiment_score": result.get("sentiment_score"),
                    "engagement_prediction": result.get("engagement_prediction"),
                    "region": result.get("region"),
                    "topics_count": len(result.get("topic_extracted", [])),
                    "emotions_count": len(result.get("emotion_analysis", [])),
                },
                "metadata": {
                    "database_status": result.get("database_status", "retrieved_from_mongo"),
                    "langgraph_status": result.get("langgraph_status", "Active"),
                },
            }

            self.collection.insert_one(log_entry)
            logger.debug("Analysis logged to MongoDB")
            return True

        except Exception as e:
            logger.error(f"Error logging to MongoDB: {e}")
            return False

    def close(self) -> None:
        """Close MongoDB connection"""
        if self.client:
            try:
                self.client.close()
                logger.info("MongoDB connection closed")
            except Exception as e:
                logger.error(f"Error closing MongoDB connection: {e}")


