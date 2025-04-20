import sqlite3
from typing import List

from langchain.tools import tool
from .db_utils import get_db_connection


@tool("get_tables_info")
def get_tables_info(tables: List[str]) -> str:
    """
    Retrieve the schema (columns, types, constraints, FKs) and the first 3 rows
    for each of the specified tables.

    Args:
        tables: A list of table names to retrieve information for.
    """
    if not tables:
        return "No tables specified."

    tables_info_parts = []
    try:
        with get_db_connection() as connection:
            cursor = connection.cursor()
            for table in tables:
                table_info_str = f"Table: `{table}`\n"
                try:
                    cursor.execute(f"PRAGMA table_info(`{table}`);")
                    schema_info = cursor.fetchall()
                    if not schema_info:
                        tables_info_parts.append(
                            f"Warning: Table '{table}' not found or has no columns."
                        )
                        continue

                    schema_details = [
                        {
                            "name": col[1],
                            "type": col[2],
                            "notnull": bool(col[3]),
                            "pk": bool(col[5]),
                        }
                        for col in schema_info
                    ]
                    table_info_str += f"Schema: {schema_details}\n"

                    cursor.execute(f"PRAGMA foreign_key_list(`{table}`);")
                    fk_info = cursor.fetchall()
                    if fk_info:
                        fk_details = [
                            {
                                "from_column": fk[3],
                                "to_table": fk[2],
                                "to_column": fk[4],
                            }
                            for fk in fk_info
                        ]
                        table_info_str += f"Foreign Keys: {fk_details}\n"

                    cursor.execute(f"SELECT * FROM `{table}` LIMIT 3;")
                    rows = cursor.fetchall()
                    column_names = [desc[0] for desc in cursor.description]
                    table_info_str += f"Sample Rows (Columns: {column_names}):\n{rows}"

                    tables_info_parts.append(table_info_str)

                except sqlite3.Error as e:
                    tables_info_parts.append(
                        f"Error retrieving info for table '{table}': {e}"
                    )

        return (
            "\n\n".join(tables_info_parts)
            if tables_info_parts
            else "Could not retrieve info for any specified table."
        )

    except sqlite3.Error as e:
        return f"Error: Could not connect to the database. {e}"
