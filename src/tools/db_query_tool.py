import sqlite3

from langchain.tools import tool
from .db_utils import _execute_query


@tool("execute_sql_query")
def db_query_tool(query: str) -> str:
    """
    Executes a **SELECT** SQL query against the SQLite database and returns the result
    including column names.
    Input should be a valid SQLite SELECT query string.
    If the query is incorrect or disallowed (not SELECT), an error message is returned.
    If an error occurs, check the schema, rewrite the query, and try again.
    **Security Note**: Only SELECT queries are permitted.
    """
    try:
        column_names, result_rows = _execute_query(query)
        if not result_rows:
            return f"Query executed successfully, but returned no results.\nColumns: {column_names}"
        else:
            return f"Query executed successfully.\nColumns: {column_names}\nResults:\n{str(result_rows)}"
    except (sqlite3.Error, PermissionError) as e:
        return f"{e}"
