from agent.utils.config_loader import load_config
from agent.utils.logger import setup_logging
from agent.utils.mongodb_logger import MongoLogger
from agent.memory.vector_store import VectorStore
from agent.analysis.analysis_engine import AnalysisEngine
from agent.workflow.agent_workflow import AgentWorkflow
from agent.api.api_server import create_app

config = load_config()
setup_logging(config)

memory_store = VectorStore(config)
analysis_engine = AnalysisEngine(config)
workflow = AgentWorkflow(memory_store, analysis_engine)
mongodb_logger = MongoLogger(config)

app = create_app(workflow, config, mongodb_logger)
