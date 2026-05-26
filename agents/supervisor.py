from state import FitnessState

def _is_filled(value) -> bool:
    return bool(value) and isinstance(value, str) and value.strip() != ""

def supervisor_node(state: FitnessState) -> dict:
    has_profile = _is_filled(state.get("user_profile"))
    has_workout = _is_filled(state.get("workout_plan"))
    has_nutrition = _is_filled(state.get("nutrition_plan"))
    has_progress = _is_filled(state.get("progress_milestones"))

    if not has_profile:
        next_agent = "goal_analyzer"
        reasoning = "user_profile is empty"
    elif not has_workout:
        next_agent = "workout_designer"
        reasoning = "workout_plan is empty"
    elif not has_nutrition:
        next_agent = "nutrition_planner"
        reasoning = "nutrition_plan is empty"
    elif not has_progress:
        next_agent = "progress_tracker"
        reasoning = "progress_milestones is empty"
    else:
        next_agent = "FINISH"
        reasoning = "all fields filled"

    print(f"[Supervisor] -> {next_agent}: {reasoning}")
    return {"next_agent": next_agent}
