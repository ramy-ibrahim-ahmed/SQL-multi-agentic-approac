# SQL execution tool with fallback to write error message in a good way for correction.
from langchain_core.runnables import RunnableLambda
from langchain_core.messages import ToolMessage
from langgraph.prebuilt import ToolNode

from ..state import State
from ..tools import db_query_tool


# When a tool error the state key 'error' will contain thre error
# so we run the handler to get that error and formate it and add it to the messages for correction
def handle_tool_error(state: State) -> State:
    error = state.get("error")
    tool_calls = state["messages"][-1].tool_calls
    return {
        "messages": [
            ToolMessage(
                content=f"Error: {repr(error)}\n please fix your mistakes.",
                tool_call_id=tc["id"],
            )
            for tc in tool_calls
        ],
    }


sql_execution_node = ToolNode([db_query_tool]).with_fallbacks(
    [RunnableLambda(handle_tool_error)], exception_key="error"
)
