from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

from config import LLM_MODEL, LLM_TEMPERATURE, GROQ_API_KEY
from rag.retriever import search_fitness_knowledge
from state import FitnessState

NUTRITION_PLANNER_PROMPT = """You are a Nutrition Planner. Design a clear
nutrition plan tailored to the user's goals and workout plan.

You have access to the search_fitness_knowledge tool. Make AT MOST 3 searches
to look up nutrition guidelines (protein intake, calorie targets, macros).
IMPORTANT: Make ONE tool call at a time.

Output format:

**Daily nutrition plan**

- **Estimated daily calories**: X kcal (with adjustment for activity)
- **Macros**:
  - Protein: X g
  - Carbs: X g
  - Fats: X g
- **Hydration**: X liters per day

**Sample daily meals**:
- Breakfast: [meal idea]
- Snack: [meal idea]
- Lunch: [meal idea]
- Snack: [meal idea]
- Dinner: [meal idea]

Respect any dietary restrictions from the user profile.
Add a note that this is educational guidance, not medical advice.

After your searches, you MUST write the final nutrition plan as your response.
"""

def nutrition_planner_node(state: FitnessState) -> dict:
    print("[NutritionPlanner] Building nutrition plan...")

    llm = ChatGroq(
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
        api_key=GROQ_API_KEY,
    ).bind_tools([search_fitness_knowledge])

    messages = [
        SystemMessage(content=NUTRITION_PLANNER_PROMPT),
        HumanMessage(content=(
            f"User profile:\n{state.get('user_profile', '')}\n\n"
            f"Workout plan:\n{state.get('workout_plan', '')}\n\n"
            f"Now design the nutrition plan."
        )),
    ]

    final_content = ""
    max_iterations = 4
    for i in range(max_iterations):
        try:
            response = llm.invoke(messages)
        except Exception as e:
            print(f"[NutritionPlanner] LLM error on iteration {i}: {type(e).__name__}")
            break

        messages.append(response)

        if response.content:
            final_content = response.content

        if not response.tool_calls:
            break

        for tool_call in response.tool_calls:
            print(f"[NutritionPlanner] searching: {tool_call['args']['query']}")
            result = search_fitness_knowledge.invoke(tool_call["args"])
            messages.append(ToolMessage(
                content=result,
                tool_call_id=tool_call["id"],
            ))

    if not final_content.strip():
        print("[NutritionPlanner] Forcing final synthesis...")
        synth_llm = ChatGroq(model=LLM_MODEL, temperature=LLM_TEMPERATURE, api_key=GROQ_API_KEY)
        synth_response = synth_llm.invoke([
            SystemMessage(content="Write a daily nutrition plan with calories, macros, and meal ideas."),
            HumanMessage(content=state.get("user_profile", "")),
        ])
        final_content = synth_response.content

    print("[NutritionPlanner] Done.")
    return {
        "nutrition_plan": final_content,
        "messages": [AIMessage(content=f"[NutritionPlanner] {final_content[:200]}...")],
    }
