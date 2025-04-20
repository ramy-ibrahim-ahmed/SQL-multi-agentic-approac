# Get schema for relevant part of the database only to reduce tokens and be more contextual.
# 1. llm decide which tables is relevant to the user question based on database tables names and columns.
# 2. invoke tool get_tables_info by only relevant tables to build the schema.
from langchain_core.messages import SystemMessage

from ..state import State, LLM
from ..tools import get_table_and_column_names, get_tables_info
from ..schemas import RelevantTables


def identify_relevant_tables(state: State) -> State:
    # Handle where no instructions
    user_instruction = state["instruction"]
    if not user_instruction:
        return {"schema": "Error: Cannot identify tables without user instruction."}

    try:
        # Get tables names and columns and handle cases
        tables_with_columns = get_table_and_column_names()

        if not tables_with_columns:
            error_message = "Error: Could not retrieve table/column names from the database. Cannot proceed."
            return {"schema": error_message}

        # Prepare tables information
        tables_columns_str = "\n".join(
            [
                f"- Table: `{name}`, Columns: {', '.join(cols)}"
                for name, cols in tables_with_columns.items()
            ]
        )

        system_prompt = (
            "You are an expert database analyst. Your task is to identify which tables "
            "from the available list are strictly necessary to answer the user's question.\n"
            "Consider the table names and their columns provided below.\n\n"
            f"Available tables and their columns:\n{tables_columns_str}\n\n"
            f"User Question (Instruction): {user_instruction}\n\n"
            "Based *only* on the table names, column names, and the user question, list the tables "
            "that seem most relevant. If multiple tables are needed (e.g., for joins), include them all. "
            "Use the 'RelevantTables' format."
        )

        # Structured output -> [str, str, ..] as tables names
        llm_tables = LLM.with_structured_output(RelevantTables)
        relevant_tables = llm_tables.invoke([SystemMessage(content=system_prompt)])

        if not relevant_tables.tables:
            return {"schema": "No relevant tables were identified for the question."}

        schema = get_tables_info.invoke({"tables": relevant_tables.tables})
        return {"schema": schema}

    except Exception as e:
        return {
            "schema": f"Error: Failed to identify relevant tables or fetch schema. Details: {e}"
        }
