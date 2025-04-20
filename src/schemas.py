from pydantic import BaseModel, Field
from typing import List, Optional


class RelevantTables(BaseModel):
    tables: List[str] = Field(
        ...,
        description="List of table names deemed relevant for answering the user's question.",
    )


class SQLQuery(BaseModel):
    sql_query: str = Field(
        ...,
        description="A syntactically correct SQLite query to address the user's question based on the provided schema.",
    )


class UserIntent(BaseModel):
    instruction: Optional[str] = Field(
        default=None,
        description="Concise English instruction for a database query agent, generated if the user input is a database query.",
    )
    response: Optional[str] = Field(
        default=None,
        description="Polite response in Arabic, generated if the user input is a greeting or not a database query.",
    )
