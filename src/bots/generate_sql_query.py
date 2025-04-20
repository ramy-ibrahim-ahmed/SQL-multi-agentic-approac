# SQL generator and corrector
# 1. If last message is tool message with error we on the correction mode.
# 2. Otherwise we are in generation mode.
# Work with limited correction retrials.
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage

from ..state import State, LLM
from ..schemas import SQLQuery


def generate_sql_query(state: State) -> State:
    # Getting state keys
    schema = state["schema"]
    instruction = state["instruction"]
    messages = state["messages"]
    last_query = state.get("last_query")

    # Check tool back with error so correction mode
    last_message = messages[-1]
    correction_mode = isinstance(last_message, ToolMessage)

    # First common part with schema which is required for both generator and corrector
    system_prompt_parts = [
        "You are an expert SQLite database engineer.",
        f"Database Schema and Sample Data:\n{schema}\n",
    ]

    # If coccrection mode add correction schema else add generation schema
    if correction_mode:
        error_details = last_message.content
        system_prompt_parts.extend(
            [
                f"The previous SQLite query attempt failed.",
                f"{error_details}",
                f"The failed query was:\n```sql\n{last_query}\n```",
                "Carefully analyze the schema, the error message, and the failed query.",
                "Provide a corrected SQLite query to address the original user instruction:",
                f"User Instruction: {instruction}\n",
                "Output *only* the corrected SQLite query using the 'SQLQuery' format.",
            ]
        )
    else:
        system_prompt_parts.extend(
            [
                "Write a precise SQLite query to answer the user's question based *only* on the provided schema and sample data.",
                f"User Question (Instruction): {instruction}\n",
                "Ensure the query is valid SQLite syntax. Use backticks (`) for table/column names if necessary.",
                "Use the 'SQLQuery' format.",
            ]
        )

    # Structure llm for produce correct string sql query
    system_prompt = "\n".join(system_prompt_parts)
    llm_sql = LLM.with_structured_output(SQLQuery)

    res = llm_sql.invoke([SystemMessage(content=system_prompt)])
    sql_query = res.sql_query

    # Add query as an arg to 'execute_sql_query'
    ai_message_with_tool_call = AIMessage(
        content="Generated SQL query, attempting execution.",
        tool_calls=[
            {
                "id": f"tool_call_{hash(sql_query)}",
                "name": "execute_sql_query",
                "args": {"query": sql_query},
            }
        ],
    )

    # Update with last query for possible correction later
    # Update error counter for max retrials
    return {
        "messages": [ai_message_with_tool_call],
        "last_query": sql_query,
        "error_count": state.get("error_count", 0) + 1,
    }
