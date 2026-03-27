"""
LangGraph Pipeline — Orchestrates the 4-agent recovery workflow.
Assessment → Policy → Solution → Execution
"""

from langgraph.graph import StateGraph, END
from models import AgentState
from agents.assessment import run_assessment
from agents.policy import run_policy
from agents.solution import run_solution
from agents.execution import run_execution


def should_continue_after_policy(state: dict) -> str:
    """
    Conditional edge after Policy Agent.
    If policy rejects, skip to end. Otherwise, continue to Solution.
    """
    if state.get("policy_approved", False):
        return "solution"
    else:
        return "end"


def build_graph():
    """
    Build and compile the LangGraph state graph.
    Returns a compiled graph ready to invoke.
    """
    graph = StateGraph(AgentState)

    # Add agent nodes
    graph.add_node("assessment", run_assessment)
    graph.add_node("policy", run_policy)
    graph.add_node("solution", run_solution)
    graph.add_node("execution", run_execution)

    # Define edges
    graph.set_entry_point("assessment")
    graph.add_edge("assessment", "policy")

    # Conditional: policy approved → solution, rejected → end
    graph.add_conditional_edges(
        "policy",
        should_continue_after_policy,
        {
            "solution": "solution",
            "end": END,
        },
    )

    graph.add_edge("solution", "execution")
    graph.add_edge("execution", END)

    # Compile
    compiled = graph.compile()
    return compiled


# Pre-build the graph for reuse
recovery_graph = build_graph()


def run_pipeline(booking: dict, disruption: dict) -> dict:
    """
    Execute the full recovery pipeline.
    Takes a booking and disruption, returns the final state.
    """
    initial_state: AgentState = {
        "booking": booking,
        "disruption": disruption,
        "assessment": "",
        "policy_approved": False,
        "policy_constraints": {},
        "alternatives": [],
        "ranked_alternatives": [],
        "selected_flight": {},
        "booking_confirmation": {},
        "sms_status": "not_sent",
        "retry_count": 0,
        "logs": ["[Pipeline] 🚀 Starting AeroResolve recovery pipeline..."],
    }

    # Run the graph
    final_state = recovery_graph.invoke(initial_state)

    return final_state
