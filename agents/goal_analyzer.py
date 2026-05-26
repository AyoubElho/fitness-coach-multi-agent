from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

from config import LLM_MODEL, LLM_TEMPERATURE, GROQ_API_KEY
from rag.retriever import search_fitness_knowledge
from state import FitnessState

GOAL_ANALYZER_PROMPT = """You are a Fitness Goal Analyzer. Your job is to
extract a structured user profile from their natural-language request.

You have access to the search_fitness_knowledge tool. Make AT MOST 2 searches
to clarify ambiguous goals or check what's realistic.
IMPORTANT: Make ONE tool call at a time.

Extract and output:
- **Primary goal**: weight loss, muscle gain, endurance, general fitness, etc.
- **Specific target**: e.g., lose 5kg, run 5K, bench press 80kg
- **Timeframe**: how many weeks/months
- **Current fitness level**: beginner, intermediate, advanced
- **Time available**: minutes per day, days per week
- **Constraints**: no gym, knee injury, dietary restrictions, etc.
- **Realistic assessment**: is the goal achievable in the timeframe?

After your searches, you MUST write the final structured profile as your response.
"""

def goal_analyzer_node(state: FitnessState) -> dict:
    print("[GoalAnalyzer] Analyzing goals...")

    llm = ChatGroq(
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
        api_key=GROQ_API_KEY,
    ).bind_tools([search_fitness_knowledge])

    messages = [
        SystemMessage(content=GOAL_ANALYZER_PROMPT),
        HumanMessage(content=f"User request: {state['user_request']}\n\nAnalyze and structure."),
    ]

    final_content = ""
    max_iterations = 4
    for i in range(max_iterations):
        try:
            response = llm.invoke(messages)
        except Exception as e:
            print(f"[GoalAnalyzer] LLM error on iteration {i}: {type(e).__name__}")
            break

        messages.append(response)

        if response.content:
            final_content = response.content

        if not response.tool_calls:
            break

        for tool_call in response.tool_calls:
            print(f"[GoalAnalyzer] searching: {tool_call['args']['query']}")
            result = search_fitness_knowledge.invoke(tool_call["args"])
            messages.append(ToolMessage(
                content=result,
                tool_call_id=tool_call["id"],
            ))

    if not final_content.strip():
        print("[GoalAnalyzer] Forcing final synthesis...")
        synth_llm = ChatGroq(model=LLM_MODEL, temperature=LLM_TEMPERATURE, api_key=GROQ_API_KEY)
        synth_response = synth_llm.invoke([
            SystemMessage(content="Write a structured user fitness profile based on the request."),
            HumanMessage(content=state["user_request"]),
        ])
        final_content = synth_response.content

    print("[GoalAnalyzer] Done.")
    return {
        "user_profile": final_content,
        "messages": [AIMessage(content=f"[GoalAnalyzer] {final_content[:200]}...")],
    }
