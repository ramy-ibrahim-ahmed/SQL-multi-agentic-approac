# Manager is the main interface for clients:
# 1. Respond to out of scope questions.
# 2. Translate the instructions from arabic to english to be easier for sql agency to do their work.
# 3. Take the query results and generate ana arabic human-like answer.
from langchain_core.messages import SystemMessage, HumanMessage

from ..state import State, LLM
from ..schemas import UserIntent


def manager(state: State) -> State:
    # Get messages and bool flage to check if this is the first invoke
    messages = state["messages"]
    is_initial_call = not state.get("instruction") and not state.get("final_answer")

    # When the first invoke prepare prompts and structured output:
    # 1. fill the final_result state with a suitable response for an out of scope question
    # --OR--
    # 2. fill the instruction state with a consise english sql instruction for sql agency
    if is_initial_call and messages and isinstance(messages[0], HumanMessage):

        system_prompt = (
            "You are an intelligent assistant processing user input for a database query system.\n"
            "Analyze the user's Arabic input. Determine if it is a database-related query or something else (like a greeting).\n\n"
            "1.  **If the input IS a database query:** Translate it accurately into a concise English instruction suitable for a database query agent. Populate the 'instruction' field.\n"
            "2.  **If the input is a greeting (e.g., 'hi', 'hello', 'السلام عليكم', 'مرحبا') OR any other non-database query:** Generate a polite, brief response *in Arabic* acknowledging the user or explaining your purpose (database queries). Populate the 'response' field.\n\n"
            f"User's Arabic Input: '{messages[0].content}'\n\n"
            "Respond using the 'UserIntent' format. Populate *only one* field: 'instruction' (for queries) or 'response' (for non-queries/greetings)."
        )

        llm_intent = LLM.with_structured_output(UserIntent)
        res = llm_intent.invoke([SystemMessage(content=system_prompt)] + messages)

        if res.instruction:
            return {"instruction": res.instruction}
        elif res.response:
            return {"final_answer": res.response}
        else:
            return {"final_answer": "عذراً، حدث خطأ غير متوقع أثناء تحليل طلبك."}

    # If not initial invoke then we are to response
    else:
        original_user_query = messages[0].content
        sql_results = messages[-1].content

        # If tool message dont has error respond with arabic answer
        if not sql_results.startswith("Error:"):
            system_prompt = (
                f"You are a helpful assistant. The user asked in Arabic: '{original_user_query}'\n\n"
                f"The following data was retrieved from the database:\n---\n{sql_results}\n---\n\n"
                "Based *strictly* on the retrieved data, provide a clear, concise, and helpful answer to the user's question in Arabic.\n"
                "Do not add any information not present in the data.\n"
                "If the data is empty ('returned no results') or doesn't directly answer the question, state that politely in Arabic.\n"
                "Answer:"
            )

        # If error say that you can not answer
        else:
            system_prompt = (
                f"You are a helpful assistant communicating in Arabic.\n"
                f"The user asked: '{original_user_query}'\n"
                f"Unfortunately, there was a problem trying to answer the question using the database.\n"
                f"The final status was: {sql_results}\n\n"
                "Politely inform the user in Arabic that their request could not be completed due to this issue. Do not suggest code."
                "Just state the problem clearly and concisely."
                "Answer:"
            )

        res = LLM.invoke([SystemMessage(content=system_prompt)])

        # return to final_answer so the router decide END
        return {"final_answer": res.content}
