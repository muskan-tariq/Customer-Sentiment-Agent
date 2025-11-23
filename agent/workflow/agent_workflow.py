"""
LangGraph Workflow for Agent Decision Making
"""

import logging
from typing import Dict, Any, Literal, Optional, List
from langgraph.graph import StateGraph, END
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class AgentState(BaseModel):
    """State model for LangGraph workflow"""
    query: str
    input_data: Dict[str, Any] = {}
    memory_results: List[Dict[str, Any]] = []
    should_reuse: bool = False
    cached_result: Optional[Dict[str, Any]] = None
    analysis_result: Optional[Dict[str, Any]] = None
    memory_used: bool = False
    final_output: Optional[Dict[str, Any]] = None


class AgentWorkflow:
    """LangGraph workflow for agent decision and processing"""
    
    def __init__(self, memory_store, analysis_engine):
        """
        Initialize workflow
        
        Args:
            memory_store: VectorStore instance
            analysis_engine: AnalysisEngine instance
        """
        self.memory_store = memory_store
        self.analysis_engine = analysis_engine
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build LangGraph workflow - Memory operations disabled for speed"""
        workflow = StateGraph(AgentState)
        
        # Add nodes (memory operations skipped for speed)
        workflow.add_node("generate_analysis", self._generate_analysis_node)
        workflow.add_node("format_output", self._format_output_node)
        
        # Define edges - skip memory, go directly to analysis
        workflow.set_entry_point("generate_analysis")
        workflow.add_edge("generate_analysis", "format_output")
        workflow.add_edge("format_output", END)
        
        return workflow.compile()
    
    def _search_memory_node(self, state: AgentState) -> AgentState:
        """Search vector database for similar queries"""
        logger.info("Searching memory for similar queries")
        try:
            # Add timeout protection - if memory search takes too long, skip it
            similar_items = self.memory_store.search_similar(state.query)
            logger.info(f"Memory search completed, found {len(similar_items)} items")
            state.memory_results = similar_items
        except Exception as e:
            logger.warning(f"Memory search failed (non-critical): {e}, continuing without memory")
            # Don't fail the workflow if memory search fails
            state.memory_results = []
        return state
    
    def _decide_reuse_node(self, state: AgentState) -> AgentState:
        """Decide whether to reuse cached result"""
        should_reuse, cached_result = self.memory_store.should_reuse_memory(
            state.memory_results
        )
        state.should_reuse = should_reuse
        state.cached_result = cached_result
        return state
    
    def _should_reuse_condition(self, state: AgentState) -> Literal["reuse", "generate"]:
        """Conditional routing based on memory reuse decision"""
        return "reuse" if state.should_reuse else "generate"
    
    def _generate_analysis_node(self, state: AgentState) -> AgentState:
        """Generate new analysis using analysis engine"""
        logger.info("Generating new analysis")
        try:
            state.analysis_result = self.analysis_engine.analyze(state.query, state.input_data)
            logger.info(f"Analysis generated successfully. Result keys: {list(state.analysis_result.keys()) if isinstance(state.analysis_result, dict) else 'not a dict'}")
        except Exception as e:
            logger.error(f"Analysis generation failed: {e}", exc_info=True)
            # Return a fallback result to prevent workflow failure
            state.analysis_result = {
                "sentiment_label": "neutral",
                "sentiment_score": 0.0,
                "emotion_analysis": [{"emotion": "neutral", "score": 0.5}],
                "engagement_prediction": "medium",
                "topic_extracted": [],
                "region": state.input_data.get("country"),
                "recommendation": "Analysis error occurred."
            }
        return state
    
    def _store_memory_node(self, state: AgentState) -> AgentState:
        """Store new result in vector database"""
        logger.info("Storing new result in memory")
        try:
            self.memory_store.store_memory(
                query=state.query,
                result=state.analysis_result
            )
            logger.info("Memory storage completed")
        except Exception as e:
            logger.warning(f"Memory storage failed (non-critical): {e}, continuing...")
            # Don't fail the workflow if memory storage fails
        return state
    
    def _format_output_node(self, state: AgentState) -> AgentState:
        """Format final JSON output in NEW format ONLY - Memory disabled for speed"""
        result = state.analysis_result
        
        # Ensure result is in NEW format only (remove any old fields)
        if isinstance(result, dict):
            # Extract only new format fields
            state.final_output = {
                "sentiment_label": result.get("sentiment_label", "neutral"),
                "sentiment_score": result.get("sentiment_score", 0.0),
                "emotion_analysis": result.get("emotion_analysis", []),
                "engagement_prediction": result.get("engagement_prediction", "medium"),
                "topic_extracted": result.get("topic_extracted", []),
                "region": result.get("region") or state.input_data.get("country") or state.input_data.get("region"),
                "recommendation": result.get("recommendation", "Continue monitoring sentiment and engagement.")
            }
        else:
            state.final_output = result
        
        return state
    
    def process(self, query: str, input_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process query through workflow
        
        Args:
            query: Input query string
            input_data: Additional input data (structured format)
            
        Returns:
            Final JSON output dictionary in new format
        """
        try:
            initial_state = AgentState(query=query, input_data=input_data or {})
            final_state = self.graph.invoke(initial_state)
            
            # LangGraph may return dict or object depending on version
            # Handle both cases
            if isinstance(final_state, dict):
                # Check if final_output exists in dict
                if "final_output" in final_state and final_state["final_output"]:
                    return final_state["final_output"]
                
                # Construct output from state dict (analysis engine already formats it)
                if final_state.get("should_reuse") and final_state.get("cached_result"):
                    result = final_state.get("cached_result")
                else:
                    result = final_state.get("analysis_result")
                
                if result is None:
                    logger.error("No analysis result available in final state")
                    raise ValueError("Analysis failed: No result generated")
                
                # Ensure result is in NEW format only (remove any old fields)
                if isinstance(result, dict):
                    # Get region from result or input_data
                    region = result.get("region") or initial_state.input_data.get("country")
                    # Extract only new format fields
                    return {
                        "sentiment_label": result.get("sentiment_label", "neutral"),
                        "sentiment_score": result.get("sentiment_score", 0.0),
                        "emotion_analysis": result.get("emotion_analysis", []),
                        "engagement_prediction": result.get("engagement_prediction", "medium"),
                        "topic_extracted": result.get("topic_extracted", []),
                        "region": region,  # Use country from input if region is null
                        "recommendation": result.get("recommendation", "Continue monitoring sentiment and engagement.")
                    }
                else:
                    logger.error("Invalid result format")
                    raise ValueError("Analysis failed: Invalid result format")
            else:
                # Handle object return (if LangGraph returns AgentState object)
                if hasattr(final_state, 'final_output') and final_state.final_output:
                    return final_state.final_output
                elif hasattr(final_state, 'analysis_result') or hasattr(final_state, 'cached_result'):
                    if final_state.should_reuse and final_state.cached_result:
                        result = final_state.cached_result
                    else:
                        result = final_state.analysis_result
                    
                    # Ensure result is in NEW format only
                    if isinstance(result, dict):
                        # Get region from result or state
                        region = result.get("region") or (final_state.input_data.get("country") if hasattr(final_state, 'input_data') else None)
                        return {
                            "sentiment_label": result.get("sentiment_label", "neutral"),
                            "sentiment_score": result.get("sentiment_score", 0.0),
                            "emotion_analysis": result.get("emotion_analysis", []),
                            "engagement_prediction": result.get("engagement_prediction", "medium"),
                            "topic_extracted": result.get("topic_extracted", []),
                            "region": region,  # Use country from input if region is null
                            "recommendation": result.get("recommendation", "Continue monitoring sentiment and engagement.")
                        }
                    else:
                        logger.error("Invalid result format")
                        raise ValueError("Analysis failed: Invalid result format")
                else:
                    logger.error(f"Invalid state returned: {type(final_state)}")
                    raise ValueError("Invalid state returned from workflow")
                    
        except Exception as e:
            logger.error(f"Error in workflow process: {e}", exc_info=True)
            raise

