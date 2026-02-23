"""Graph assembly and routing for the triage agent."""

from langgraph.graph import StateGraph, END

from state import TriageAgentState
from nodes import (
    parse_patient_message,
    assess_urgency,
    emergency_handler,
    urgent_handler,
    routine_handler,
    generate_response,
)


def route_by_urgency(state: TriageAgentState) -> str:
    """Route to handler based on urgency level."""
    level = state.get("urgency_level", "ROUTINE")
    if level == "EMERGENCY":
        return "emergency"
    elif level == "URGENT":
        return "urgent"
    return "routine"


def build_graph():
    """Construct and compile the triage agent graph."""
    graph = StateGraph(TriageAgentState)

    graph.add_node("parse_patient_message", parse_patient_message)
    graph.add_node("assess_urgency", assess_urgency)
    graph.add_node("emergency", emergency_handler)
    graph.add_node("urgent", urgent_handler)
    graph.add_node("routine", routine_handler)
    graph.add_node("generate_response", generate_response)

    graph.set_entry_point("parse_patient_message")
    graph.add_edge("parse_patient_message", "assess_urgency")

    graph.add_conditional_edges(
        "assess_urgency",
        route_by_urgency,
        {"emergency": "emergency", "urgent": "urgent", "routine": "routine"},
    )

    graph.add_edge("emergency", "generate_response")
    graph.add_edge("urgent", "generate_response")
    graph.add_edge("routine", "generate_response")
    graph.add_edge("generate_response", END)

    return graph.compile()


agent = build_graph()
