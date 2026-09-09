"""
test_prioritizer.py: Unit tests for skill gap ranking and urgency categorization.
"""

from skilltrace_ai.prioritizer import prioritize_skill_gaps


def test_prioritization_ordering():
    gaps = [
        {"name": "SQL", "required_level": 4, "student_level": 3},      # deficit=1, score=4 -> LOW
        {"name": "Power BI", "required_level": 4, "student_level": 0}, # deficit=4, score=16 -> HIGH
        {"name": "Excel", "required_level": 4, "student_level": 2},    # deficit=2, score=8 -> MEDIUM
    ]

    prioritized = prioritize_skill_gaps(gaps)
    assert len(prioritized) == 3

    # Rank 1 must be Power BI (score 16)
    assert prioritized[0]["name"] == "Power BI"
    assert prioritized[0]["urgency"] == "HIGH"
    assert prioritized[0]["rank"] == 1

    # Rank 2 must be Excel (score 8)
    assert prioritized[1]["name"] == "Excel"
    assert prioritized[1]["urgency"] == "MEDIUM"
    assert prioritized[1]["rank"] == 2

    # Rank 3 must be SQL (score 4)
    assert prioritized[2]["name"] == "SQL"
    assert prioritized[2]["urgency"] == "LOW"
    assert prioritized[2]["rank"] == 3


def test_prioritization_empty_gaps():
    assert prioritize_skill_gaps([]) == []
