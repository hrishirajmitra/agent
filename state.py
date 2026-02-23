"""State definition for the triage agent."""

from typing import TypedDict


class TriageAgentState(TypedDict):
    # Input
    patient_message: str
    patient_id: str
    patient_age: int
    known_conditions: list[str]

    # Populated by nodes
    symptoms: list[str]
    duration: str
    severity_score: int           # 1-10
    urgency_level: str            # EMERGENCY | URGENT | ROUTINE
    red_flags: list[str]
    confidence: float

    # Output
    response: str
    action_taken: str             # ESCALATE | BOOK | SELF_CARE
    escalation_reason: str
