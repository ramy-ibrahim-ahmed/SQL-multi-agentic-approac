from langgraph.graph import StateGraph, END

from .routers import route_after_manager, should_regenerate_query
from .bots import manager, identify_relevant_tables
from .bots import generate_sql_query, sql_execution_node
from .state import State

workflow = StateGraph(State)

workflow.add_node("manager", manager)
workflow.add_node("identify_relevant_tables", identify_relevant_tables)
workflow.add_node("generate_sql_query", generate_sql_query)
workflow.add_node("execute_sql", sql_execution_node)

workflow.set_entry_point("manager")

workflow.add_conditional_edges(
    "manager",
    route_after_manager,
    {
        "identify_relevant_tables": "identify_relevant_tables",
        END: END,
    },
)

workflow.add_edge("identify_relevant_tables", "generate_sql_query")
workflow.add_edge("generate_sql_query", "execute_sql")

workflow.add_conditional_edges(
    "execute_sql",
    should_regenerate_query,
    {
        "generate_sql_query": "generate_sql_query",
        "manager": "manager",
    },
)

GRAPH = workflow.compile()


# from IPython.display import display, Markdown

# initial_state = State(messages=[HumanMessage(content="كم عدد المقررات الموجودة؟")])
# for event in GRAPH.stream(initial_state, {"recursion_limit": 50}):
#     print(event)

# {"manager": {"instruction": "How many courses are available?"}}
# {
#     "identify_relevant_tables": {
#         "schema": "Table: `courses`\nSchema: [{'name': 'course_id', 'type': 'INTEGER', 'notnull': False, 'pk': True}, {'name': 'name', 'type': 'TEXT', 'notnull': True, 'pk': False}, {'name': 'department_id', 'type': 'INTEGER', 'notnull': False, 'pk': False}, {'name': 'teacher_id', 'type': 'INTEGER', 'notnull': False, 'pk': False}]\nForeign Keys: [{'from_column': 'teacher_id', 'to_table': 'teachers', 'to_column': 'teacher_id'}, {'from_column': 'department_id', 'to_table': 'departments', 'to_column': 'department_id'}]\nSample Rows (Columns: ['course_id', 'name', 'department_id', 'teacher_id']):\n[(1, 'Introduction to Programming', 1, 1), (2, 'Data Structures', 1, 6), (3, 'Calculus I', 2, 2)]"
#     }
# }
# {
#     "generate_sql_query": {
#         "messages": [
#             AIMessage(
#                 content="Generated SQL query, attempting execution.",
#                 additional_kwargs={},
#                 response_metadata={},
#                 id="9327efca-9264-4590-ab04-c3f0225d9c39",
#                 tool_calls=[
#                     {
#                         "name": "execute_sql_query",
#                         "args": {"query": "SELECT COUNT(*) FROM courses"},
#                         "id": "tool_call_6252672957696160681_0",
#                         "type": "tool_call",
#                     }
#                 ],
#             )
#         ],
#         "error_count": 0,
#         "last_query": "SELECT COUNT(*) FROM courses",
#     }
# }
# {
#     "execute_sql": {
#         "messages": [
#             ToolMessage(
#                 content="Query executed successfully.\nColumns: ['COUNT(*)']\nResults:\n[(8,)]",
#                 name="execute_sql_query",
#                 id="8c7047e6-99a2-4f23-ad72-143621102847",
#                 tool_call_id="tool_call_6252672957696160681_0",
#             )
#         ]
#     }
# }
# {"manager": {"final_answer": "عدد المقررات الموجودة هو 8."}}


# ##############################################################################################


# initial_state = State(messages=[HumanMessage(content="شكراً لك")])
# for event in GRAPH.stream(initial_state, {"recursion_limit": 50}):
#     print(event)

# {"manager": {"final_answer": "على الرحب والسعة! كيف يمكنني مساعدتك اليوم؟"}}
