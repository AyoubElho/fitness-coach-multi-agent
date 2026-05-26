from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from state import FitnessState
from agents.supervisor import supervisor_node
from agents.goal_analyzer import goal_analyzer_node
from agents.workout_designer import workout_designer_node
from agents.nutrition_planner import nutrition_planner_node
from agents.progress_tracker import progress_tracker_node

def route_from_supervisor(state: FitnessState) -> str:
    next_agent = state.get("next_agent", "FINISH")
    if next_agent == "FINISH":
        return END
    return next_agent

def build_graph():
    workflow = StateGraph(FitnessState)

    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("goal_analyzer", goal_analyzer_node)
    workflow.add_node("workout_designer", workout_designer_node)
    workflow.add_node("nutrition_planner", nutrition_planner_node)
    workflow.add_node("progress_tracker", progress_tracker_node)

    workflow.add_edge(START, "supervisor")

    workflow.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "goal_analyzer": "goal_analyzer",
            "workout_designer": "workout_designer",
            "nutrition_planner": "nutrition_planner",
            "progress_tracker": "progress_tracker",
            END: END,
        },
    )

    workflow.add_edge("goal_analyzer", "supervisor")
    workflow.add_edge("workout_designer", "supervisor")
    workflow.add_edge("nutrition_planner", "supervisor")
    workflow.add_edge("progress_tracker", "supervisor")

    checkpointer = MemorySaver()
    return workflow.compile(checkpointer=checkpointer)

graph = build_graph()

def run_cli():
    from langgraph.types import Command

    user_request = input("Fitness goal: ")
    config = {"configurable": {"thread_id": "demo-1"}}

    initial_state = {
        "user_request": user_request,
        "messages": [],
    }

    for event in graph.stream(initial_state, config=config):
        for node_name, node_output in event.items():
            if node_name == "__interrupt__":
                print("\n=== HUMAN APPROVAL NEEDED ===")
                interrupt_data = node_output[0].value
                print(interrupt_data["full_plan"])
                user_decision = input("\nApprove? (yes/no): ")
                for resumed_event in graph.stream(
                    Command(resume=user_decision), config=config
                ):
                    print(resumed_event)

if __name__ == "__main__":
    run_cli()
