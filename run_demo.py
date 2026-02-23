"""Demo runner for the triage agent."""

from graph import agent


SCENARIOS = [
    {
        "title": "EMERGENCY -- Chest Pain",
        "input": {
            "patient_message": "I've had chest pain and left arm tingling for the past 20 minutes",
            "patient_id": "PAT-001",
            "patient_age": 55,
            "known_conditions": ["hypertension"],
            "symptoms": [],
            "duration": "",
            "severity_score": 0,
            "urgency_level": "",
            "red_flags": [],
            "confidence": 0.0,
            "response": "",
            "action_taken": "",
            "escalation_reason": "",
        },
    },
    {
        "title": "URGENT -- Sore Throat & Fever",
        "input": {
            "patient_message": "I've had a sore throat and low fever since yesterday, feels worse today",
            "patient_id": "PAT-002",
            "patient_age": 32,
            "known_conditions": [],
            "symptoms": [],
            "duration": "",
            "severity_score": 0,
            "urgency_level": "",
            "red_flags": [],
            "confidence": 0.0,
            "response": "",
            "action_taken": "",
            "escalation_reason": "",
        },
    },
    {
        "title": "ROUTINE -- Mild Headache",
        "input": {
            "patient_message": "Mild headache for a few hours, probably from staring at screens",
            "patient_id": "PAT-003",
            "patient_age": 24,
            "known_conditions": [],
            "symptoms": [],
            "duration": "",
            "severity_score": 0,
            "urgency_level": "",
            "red_flags": [],
            "confidence": 0.0,
            "response": "",
            "action_taken": "",
            "escalation_reason": "",
        },
    },
]


def run_scenario(title, patient_input):
    """Run a single scenario and print results."""
    separator = "=" * 70
    print(f"\n{separator}")
    print(f"  SCENARIO: {title}")
    print(separator)
    print(f"  Message: \"{patient_input['patient_message']}\"")
    print(f"  Patient: {patient_input['patient_id']}, Age {patient_input['patient_age']}")
    print(f"  Known conditions: {', '.join(patient_input['known_conditions']) or 'None'}")
    print("-" * 70)

    result = agent.invoke(patient_input)

    print(f"\n  {'Step':<25} Output")
    print(f"  {'-'*25} {'-'*42}")
    print(f"  {'parse_message':<25} symptoms: {result.get('symptoms', [])}")
    print(f"  {'':<25} duration: {result.get('duration', 'N/A')}")
    print(f"  {'assess_urgency':<25} severity: {result.get('severity_score', 'N/A')}/10")
    print(f"  {'':<25} level: {result.get('urgency_level', 'N/A')}")
    print(f"  {'':<25} red_flags: {result.get('red_flags', [])}")
    print(f"  {'':<25} confidence: {result.get('confidence', 'N/A')}")
    print(f"  {'route':<25} -> {result.get('urgency_level', 'N/A').lower()} node")
    print(f"  {'action':<25} {result.get('action_taken', 'N/A')}")

    if result.get("escalation_reason"):
        print(f"  {'details':<25} {result['escalation_reason']}")

    print(f"\n  PATIENT RESPONSE")
    print(f"  {'-'*68}")
    for line in result.get("response", "No response generated.").split("\n"):
        print(f"  {line}")
    print(f"  {'-'*68}")

    return result


def main():
    print("\n" + "=" * 70)
    print("  PATIENT SYMPTOM TRIAGE AGENT -- DEMO")
    print("=" * 70)
    print("\n  DISCLAIMER: This is a demo. The agent does NOT provide medical")
    print("  diagnoses. A human clinician always owns the final decision.\n")

    for scenario in SCENARIOS:
        run_scenario(scenario["title"], scenario["input"])

    print(f"\n{'='*70}")
    print("  All scenarios completed.")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
