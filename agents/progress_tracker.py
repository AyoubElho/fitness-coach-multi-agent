from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.types import interrupt

from config import LLM_MODEL, LLM_TEMPERATURE, GROQ_API_KEY
from state import FitnessState

PROGRESS_TRACKER_PROMPT = """You are a Progress Tracker. Define clear,
measurable milestones to track the user's progress toward their goal.

Output format:

**Progress milestones**

- **Week 2 checkpoint**: [what to measure / what should be true]
- **Week 4 checkpoint**: [what to measure / what should be true]
- **Mid-point checkpoint**: [what to measure / what should be true]
- **Final checkpoint**: [what to measure / what should be true]

**Metrics to track weekly**:
- Body metrics (weight, measurements, photos)
- Performance metrics (workout completion, weights lifted, distance/time)
- Subjective metrics (energy, sleep, mood)

Make milestones realistic given the user's timeframe and starting fitness level.
"""

def progress_tracker_node(state: FitnessState) -> dict:
    print("[ProgressTracker] Building milestones...")

    llm = ChatGroq(
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
        api_key=GROQ_API_KEY,
    )

    response = llm.invoke([
        SystemMessage(content=PROGRESS_TRACKER_PROMPT),
        HumanMessage(content=(
            f"User profile:\n{state.get('user_profile', '')}\n\n"
            f"Workout plan:\n{state.get('workout_plan', '')}\n\n"
            f"Nutrition plan:\n{state.get('nutrition_plan', '')}\n\n"
            f"Now define progress milestones."
        )),
    ])

    milestones = response.content
    print("[ProgressTracker] Milestones ready. Pausing for human approval...")

    plan_summary = (
        f"**Goal & Profile:**\n{state.get('user_profile', '')}\n\n"
        f"**Workout Plan:**\n{state.get('workout_plan', '')}\n\n"
        f"**Nutrition Plan:**\n{state.get('nutrition_plan', '')}\n\n"
        f"**Progress Milestones:**\n{milestones}"
    )

    human_response = interrupt({
        "type": "approval_required",
        "full_plan": plan_summary,
        "question": "Do you approve this fitness plan and commit to following it?",
    })

    approved = str(human_response).strip().lower() in ("yes", "y", "approve", "true")

    if approved:
        final_message = "Plan approved! You're committed. Good luck — stay consistent."
    else:
        final_message = "Plan not approved. Adjust the inputs and try again."

    print(f"[ProgressTracker] User decision: {'APPROVED' if approved else 'REJECTED'}")
    return {
        "progress_milestones": milestones,
        "plan_approved": approved,
        "messages": [AIMessage(content=final_message)],
    }
