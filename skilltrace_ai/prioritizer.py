"""
prioritizer.py: Explainable skill gap prioritization ranking.
Formula:
  deficit = max(0, required_level - student_level)
  priority_score = deficit * required_level
Tier classification:
  - HIGH: priority_score >= 12 or (missing and required_level >= 4)
  - MEDIUM: priority_score between 6 and 11
  - LOW: priority_score < 6
"""

from typing import Any, Dict, List


def prioritize_skill_gaps(gaps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Ranks missing and partial skill gaps by severity and criticality.
    Returns prioritized list sorted from highest urgency to lowest urgency.
    """
    prioritized = []

    for gap in gaps:
        req = max(1, gap.get("required_level", 1))
        stu = max(0, gap.get("student_level", 0))
        deficit = max(0, req - stu)

        # Skip if no deficit exists
        if deficit <= 0:
            continue

        priority_score = deficit * req

        if priority_score >= 12 or (stu == 0 and req >= 4):
            urgency = "HIGH"
        elif priority_score >= 6:
            urgency = "MEDIUM"
        else:
            urgency = "LOW"

        prioritized.append({
            "name": gap.get("name", "Unknown"),
            "category": gap.get("category", "gap"),
            "student_level": stu,
            "required_level": req,
            "deficit": deficit,
            "priority_score": priority_score,
            "urgency": urgency,
            "rationale": (
                f"Deficit of {deficit} level(s) on a key skill required at Level {req}."
            ),
        })

    # Sort descending by priority_score, then deficit
    prioritized.sort(key=lambda x: (x["priority_score"], x["deficit"]), reverse=True)

    # Assign rank
    for index, item in enumerate(prioritized, start=1):
        item["rank"] = index

    return prioritized
