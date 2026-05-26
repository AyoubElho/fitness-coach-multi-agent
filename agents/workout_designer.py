from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

from config import LLM_MODEL, LLM_TEMPERATURE, GROQ_API_KEY
from rag.retriever import search_fitness_knowledge
from state import FitnessState

WORKOUT_DESIGNER_PROMPT = """You are a Workout Designer. Build a clear,
realistic weekly training plan based on the user's profile.

You have access to the search_fitness_knowledge tool. Make AT MOST 3 searches
to look up exercise specifics, training principles, or recovery guidelines.
IMPORTANT: Make ONE tool call at a time.

Output format:

**Weekly workout plan**

For each day of the week:
- **Day N (Monday/Tuesday/...)**: workout type
  - Exercises: [list with sets x reps or duration]
  - Estimated time: X minutes
  - Intensity: low / moderate / high

Include at least 1 rest or active-recovery day. Respect the user's
time and equipment constraints from the profile.

After your searches, you MUST write the final weekly plan as your response.
"""

def workout_designer_node(state: FitnessState) -> dict:
    print("[WorkoutDesigner] Building workout plan...")

    llm = ChatGroq(
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
        api_key=GROQ_API_KEY,
    ).bind_tools([search_fitness_knowledge])

    messages = [
        SystemMessage(content=WORKOUT_DESIGNER_PROMPT),
        HumanMessage(content=(
            f"User request: {state['user_request']}\n\n"
            f"User profile:\n{state.get('user_profile', '')}\n\n"
            f"Now design the weekly workout plan."
        )),
    ]

    final_content = ""
    max_iterations = 4
    for i in range(max_iterations):
        try:
            response = llm.invoke(messages)
        except Exception as e:
            print(f"[WorkoutDesigner] LLM error on iteration {i}: {type(e).__name__}")
            break

        messages.append(response)

        if response.content:
            final_content = response.content

        if not response.tool_calls:
            break

        for tool_call in response.tool_calls:
            print(f"[WorkoutDesigner] searching: {tool_call['args']['query']}")
            result = search_fitness_knowledge.invoke(tool_call["args"])
            messages.append(ToolMessage(
                content=result,
                tool_call_id=tool_call["id"],
            ))

    if not final_content.strip():
        print("[WorkoutDesigner] Forcing final synthesis...")
        synth_llm = ChatGroq(model=LLM_MODEL, temperature=LLM_TEMPERATURE, api_key=GROQ_API_KEY)
        synth_response = synth_llm.invoke([
            SystemMessage(content="Write a weekly workout plan for the user described below."),
            HumanMessage(content=state.get("user_profile", "")),
        ])
        final_content = synth_response.content

    print("[WorkoutDesigner] Done.")
    return {
        "workout_plan": final_content,
        "messages": [AIMessage(content=f"[WorkoutDesigner] {final_content[:200]}...")],
    }
