# 1. router for error handle with fallback.
# 2. router after manager tp go end with final_answer generated, or sql agency.
from langchain_core.messages import ToolMessage
from langgraph.graph import END

from .state import State, MAX_QUERY_RETRIES


def should_regenerate_query(state: State) -> str:
    messages = state["messages"]
    error_count = state.get("error_count", 0)
    last_message = messages[-1]

    # If last message is tool with error and in the valid retries range
    # go to correction else manager.
    if (
        isinstance(last_message, ToolMessage)
        and last_message.content.startswith("Error:")
        and error_count <= MAX_QUERY_RETRIES
    ):
        return "generate_sql_query"
    else:
        return "manager"


def route_after_manager(state: State) -> str:
    if state.get("final_answer"):
        return END
    elif state.get("instruction"):
        return "identify_relevant_tables"
