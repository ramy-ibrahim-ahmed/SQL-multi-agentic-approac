import logging
from typing import Optional

from langchain_ollama.chat_models import ChatOllama
from langgraph.graph import MessagesState

DB_PATH = r"C:\Users\ramyu\code\sql-agent\lms.db"
LLM_MODEL = "qwen2.5:7b"
MAX_QUERY_RETRIES = 2
LOG_LEVEL = logging.INFO

logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s - %(levelname)s - %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


class State(MessagesState):
    instruction: Optional[str] = None
    response: Optional[str] = None
    schema: Optional[str] = None
    error_count: int = 0
    last_query: Optional[str] = None
    final_answer: Optional[str] = None


LLM = ChatOllama(model=LLM_MODEL, temperature=0.0)
