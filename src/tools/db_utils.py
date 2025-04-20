import sqlite3
from typing import Dict, List, Tuple

from ..state import logger, DB_PATH


def get_db_connection() -> sqlite3.Connection:
    try:
        return sqlite3.connect(DB_PATH)
    except sqlite3.Error as e:
        raise


def get_table_and_column_names() -> Dict[str, List[str]]:
    tables_columns = {}
    try:
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [table[0] for table in cursor.fetchall()]
            for table in tables:
                try:
                    cursor.execute(f"PRAGMA table_info(`{table}`);")
                    columns = [col[1] for col in cursor.fetchall()]
                    tables_columns[table] = columns
                except sqlite3.Error as e:
                    logger.warning(f"Could not get columns for table '{table}': {e}")
            return tables_columns
    except sqlite3.Error as e:
        return {}


def _execute_query(query: str) -> Tuple[str, List[tuple]]:
    if "SELECT" not in query.strip().upper():
        raise PermissionError("Error: Only SELECT queries are permitted for execution.")

    try:
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            column_names = (
                [desc[0] for desc in cursor.description] if cursor.description else []
            )
            return column_names, results
    except sqlite3.Error as e:
        raise sqlite3.Error(f"Error: Query failed. Details: {e}") from e
