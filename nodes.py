"""Node functions for the triage agent graph."""

import json
import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from state import TriageAgentState

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemma-3-4b-it",
    temperature=0.1,
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)


def _parse_json(text: str, fallback: dict) -> dict:
    """Extract JSON from LLM response text."""
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass
    return fallback


# -- Node 1: Parse patient message --

def parse_patient_message(state: TriageAgentState) -> dict:
    """Extract symptoms, duration, and severity cues from free-text."""
    system_prompt = (
        "You are a medical intake assistant. Extract structured information "
        "from a patient's message. Do NOT diagnose.\n\n"
        "Return ONLY valid JSON (no markdown, no code fences):\n"
        '{"symptoms": ["list of symptoms"], '
        '"duration": "how long", '
        '"severity_cues": ["severity language"]}\n\n'
        "If duration is not mentioned, use 'not specified'."
    )

    patient_context = (
        f"Patient ID: {state.get('patient_id', 'unknown')}\n"
        f"Age: {state.get('patient_age', 'unknown')}\n"
        f"Known conditions: {', '.join(state.get('known_conditions', [])) or 'None'}\n\n"
        f"Patient message: \"{state['patient_message']}\""
    )

    response = llm.invoke([
        HumanMessage(content=f"{system_prompt}\n\n{patient_context}"),
    ])

    parsed = _parse_json(response.content, {
        "symptoms": ["unable to parse"],
        "duration": "not specified",
        "severity_cues": [],
    })

    return {
        "symptoms": parsed.get("symptoms", []),
        "duration": parsed.get("duration", "not specified"),
    }


# -- Node 2: Assess urgency --

def assess_urgency(state: TriageAgentState) -> dict:
    """Evaluate urgency with red-flag detection and severity scoring."""
    system_prompt = (
        "You are a medical triage assistant. You do NOT diagnose. "
        "Assess urgency to route the patient.\n\n"
        "RED FLAGS: chest pain with radiating pain, difficulty breathing, "
        "sudden severe headache, stroke signs, severe abdominal pain, "
        "high fever with stiff neck, uncontrolled bleeding, "
        "loss of consciousness, severe allergic reaction, suicidal ideation.\n\n"
        "LEVELS:\n"
        "- EMERGENCY (8-10): red flags, potential life threat\n"
        "- URGENT (4-7): needs same-day attention, worsening\n"
        "- ROUTINE (1-3): mild, self-care appropriate\n\n"
        "Consider patient age and known conditions.\n\n"
        "Return ONLY valid JSON (no markdown, no code fences):\n"
        '{"severity_score": <1-10>, "urgency_level": "EMERGENCY|URGENT|ROUTINE", '
        '"red_flags": ["list"], "confidence": <0.0-1.0>, '
        '"reasoning": "brief explanation"}'
    )

    assessment_input = (
        f"Patient age: {state.get('patient_age', 'unknown')}\n"
        f"Known conditions: {', '.join(state.get('known_conditions', [])) or 'None'}\n"
        f"Symptoms: {', '.join(state.get('symptoms', []))}\n"
        f"Duration: {state.get('duration', 'not specified')}\n"
        f"Original message: \"{state['patient_message']}\""
    )

    response = llm.invoke([
        HumanMessage(content=f"{system_prompt}\n\n{assessment_input}"),
    ])

    assessed = _parse_json(response.content, {
        "severity_score": 6,
        "urgency_level": "URGENT",
        "red_flags": [],
        "confidence": 0.3,
    })

    return {
        "severity_score": assessed.get("severity_score", 5),
        "urgency_level": assessed.get("urgency_level", "URGENT"),
        "red_flags": assessed.get("red_flags", []),
        "confidence": assessed.get("confidence", 0.5),
    }


# -- Node 4a: Emergency handler --

def emergency_handler(state: TriageAgentState) -> dict:
    """Flag for on-call staff, log high-priority ticket."""
    red_flags_str = ", ".join(state.get("red_flags", []))
    escalation_reason = (
        f"EMERGENCY TRIAGE -- Severity {state.get('severity_score', 'N/A')}/10. "
        f"Red flags: {red_flags_str or 'elevated risk'}. "
        f"Patient (ID: {state.get('patient_id', 'unknown')}, "
        f"Age: {state.get('patient_age', 'unknown')}) "
        f"requires immediate clinical review."
    )

    print("  [SIMULATED] Alerting on-call medical staff")
    print("  [SIMULATED] Creating HIGH PRIORITY ticket")
    print("  [SIMULATED] Sending SMS to on-call physician")

    return {
        "action_taken": "ESCALATE",
        "escalation_reason": escalation_reason,
    }


# -- Node 4b: Urgent handler --

def urgent_handler(state: TriageAgentState) -> dict:
    """Book same-day appointment."""
    now = datetime.now()
    slot = now.replace(hour=15, minute=0, second=0, microsecond=0)
    if slot <= now:
        slot += timedelta(days=1)

    slot_str = slot.strftime(
        "%I:%M %p today" if slot.date() == now.date() else "%I:%M %p tomorrow"
    )

    print("  [SIMULATED] Checking appointment availability")
    print(f"  [SIMULATED] Same-day slot found: {slot_str}")
    print(f"  [SIMULATED] Booking confirmed for patient {state.get('patient_id', 'unknown')}")

    return {
        "action_taken": "BOOK",
        "escalation_reason": (
            f"Same-day appointment booked for {slot_str}. "
            f"Severity: {state.get('severity_score', 'N/A')}/10."
        ),
    }


# -- Node 4c: Routine handler --

def routine_handler(state: TriageAgentState) -> dict:
    """Provide self-care guidance."""
    print("  [SIMULATED] Generating self-care guidance")
    print(f"  [SIMULATED] Logging routine triage for patient {state.get('patient_id', 'unknown')}")

    return {
        "action_taken": "SELF_CARE",
        "escalation_reason": "",
    }


# -- Node 5: Generate response --

def generate_response(state: TriageAgentState) -> dict:
    """Assemble patient-facing message."""
    system_prompt = (
        "You are a compassionate healthcare communication assistant.\n\n"
        "Rules:\n"
        "- NEVER diagnose or suggest a specific medical condition\n"
        "- NEVER invent specific details not mentioned by the patient (e.g., numeric pain levels like '7/10')\n"
        "- DO NOT mention internal severity scores (1-10) in the patient message\n"
        "- Summarize what you understood using the patient's own language\n"
        "- State what action is being taken clearly\n"
        "- Always include guidance on what to do if symptoms worsen\n"
        "- Be empathetic but concise\n"
        "- If the action is ESCALATE, emphasize urgency without causing panic\n\n"
        "Write the message directly — do NOT include any JSON or formatting markers."
    )

    context = (
        f"Symptoms: {', '.join(state.get('symptoms', []))}\n"
        f"Duration: {state.get('duration', 'not specified')}\n"
        f"Severity: {state.get('severity_score', 'N/A')}/10\n"
        f"Urgency: {state.get('urgency_level', 'ROUTINE')}\n"
        f"Red flags: {', '.join(state.get('red_flags', [])) or 'None'}\n"
        f"Action taken: {state.get('action_taken', 'SELF_CARE')}\n"
        f"Details: {state.get('escalation_reason', '')}\n"
        f"Patient age: {state.get('patient_age', 'unknown')}\n"
        f"Known conditions: {', '.join(state.get('known_conditions', [])) or 'None'}\n\n"
        f"Generate the patient-facing message now."
    )

    response = llm.invoke([
        HumanMessage(content=f"{system_prompt}\n\n{context}"),
    ])

    return {"response": response.content.strip()}
