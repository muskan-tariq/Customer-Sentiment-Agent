"""
Vector Database Integration using ChromaDB
Handles embedding generation, similarity search, and memory storage
Uses sentence-transformers for free local embeddings
"""

import os
import json
import logging
import time
import uuid
from typing import List, Dict, Optional, Tuple
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class VectorStore:
    """Manages long-term memory using ChromaDB vector database"""
    
    def __init__(self, config: Dict):
        """
        Initialize vector store
        
        Args:
            config: Configuration dictionary with vector_db and embeddings settings
        """
        self.config = config
        embedding_model_name = config.get("embeddings", {}).get("model", "all-MiniLM-L6-v2")
        
        # Initialize sentence-transformers model (local, free)
        logger.info(f"Loading embedding model: {embedding_model_name}")
        self.embedding_model = SentenceTransformer(embedding_model_name)
        logger.info("Embedding model loaded successfully")
        
        self.similarity_threshold = config.get("vector_db", {}).get("similarity_threshold", 0.75)
        
        # Initialize ChromaDB
        persist_dir = config.get("vector_db", {}).get("persist_directory", "./data/chroma_db")
        os.makedirs(persist_dir, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(anonymized_telemetry=False)
        )
        
        collection_name = config.get("vector_db", {}).get("collection_name", "sentiment_memory")
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info(f"Vector store initialized with collection: {collection_name}")
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using sentence-transformers (local, free)"""
        try:
            # sentence-transformers generates embeddings locally
            embedding = self.embedding_model.encode(text, convert_to_numpy=True).tolist()
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def search_similar(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Search for similar past queries in vector database
        
        Args:
            query: Input query string
            top_k: Number of similar results to return
            
        Returns:
            List of similar past queries with metadata
        """
        try:
            query_embedding = self._generate_embedding(query)
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            similar_items = []
            if results["ids"] and len(results["ids"][0]) > 0:
                for i, doc_id in enumerate(results["ids"][0]):
                    distance = results["distances"][0][i] if results["distances"] else None
                    similarity = 1 - distance if distance is not None else 0
                    
                    if similarity >= self.similarity_threshold:
                        metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                        document = results["documents"][0][i] if results["documents"] else ""
                        
                        similar_items.append({
                            "id": doc_id,
                            "query": document,
                            "similarity": similarity,
                            "result": json.loads(metadata.get("result", "{}")),
                            "metadata": metadata
                        })
            
            logger.info(f"Found {len(similar_items)} similar items for query")
            return similar_items
            
        except Exception as e:
            logger.error(f"Error searching similar queries: {e}")
            return []
    
    def store_memory(self, query: str, result: Dict, metadata: Optional[Dict] = None) -> str:
        """
        Store new query and result in vector database
        
        Args:
            query: Input query string
            result: Analysis result dictionary
            metadata: Additional metadata to store
            
        Returns:
            Document ID of stored item
        """
        try:
            query_embedding = self._generate_embedding(query)
            
            # Generate unique ID
            doc_id = str(uuid.uuid4())
            
            # Prepare metadata
            store_metadata = {
                "result": json.dumps(result),
                "timestamp": str(int(time.time())),
            }
            if metadata:
                store_metadata.update(metadata)
            
            # Store in ChromaDB
            self.collection.add(
                ids=[doc_id],
                embeddings=[query_embedding],
                documents=[query],
                metadatas=[store_metadata]
            )
            
            logger.info(f"Stored new memory with ID: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Error storing memory: {e}")
            raise
    
    def should_reuse_memory(self, similar_items: List[Dict]) -> Tuple[bool, Optional[Dict]]:
        """
        Decide whether to reuse memory based on similarity threshold
        
        Args:
            similar_items: List of similar items from search
            
        Returns:
            Tuple of (should_reuse, best_match_result)
        """
        if not similar_items:
            return False, None
        
        # Get the most similar item
        best_match = max(similar_items, key=lambda x: x["similarity"])
        
        if best_match["similarity"] >= self.similarity_threshold:
            logger.info(f"Reusing memory with similarity: {best_match['similarity']:.3f}")
            return True, best_match["result"]
        
        return False, None

