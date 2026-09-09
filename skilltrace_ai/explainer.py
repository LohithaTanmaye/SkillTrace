"""
explainer.py: Generates natural language explanations of alignment results,
transparent scoring mechanics, and required ethical disclaimers.
"""

from typing import Any, Dict, List

STANDARD_DISCLAIMER = (
    "The match score is an estimate of skill alignment based on the available "
    "assessment/profile data and job requirements. It does not guarantee job "
    "suitability or employment."
)


def generate_explanation(
    match_score: float,
    matched_skills: List[Dict[str, Any]],
    partial_gaps: List[Dict[str, Any]],
    missing_skills: List[Dict[str, Any]],
    prioritized_gaps: List[Dict[str, Any]],
    job_title: str = "this target role",
) -> Dict[str, Any]:
    """
    Creates an interpretable natural language narrative explaining:
    - Strengths (matched skills)
    - Areas requiring upskilling (partial gaps)
    - Missing prerequisites
    - Immediate next step
    - Transparent score mechanics
    - Ethical disclaimer
    """
    matched_names = [s.get("name", "") for s in matched_skills]
    partial_names = [s.get("name", "") for s in partial_gaps]
    missing_names = [s.get("name", "") for s in missing_skills]

    # Build human-readable narrative
    narrative_parts = []

    if matched_names:
        matched_str = ", ".join(matched_names)
        narrative_parts.append(
            f"Your current skill profile strongly matches {matched_str} requirements for {job_title}."
        )
    else:
        narrative_parts.append(
            f"Your profile does not yet meet the full baseline requirements for {job_title}."
        )

    if partial_names and missing_names:
        narrative_parts.append(
            f"However, {', '.join(partial_names)} fall(s) below the expected proficiency, "
            f"and {', '.join(missing_names)} is currently missing from your profile."
        )
    elif partial_names:
        narrative_parts.append(
            f"However, {', '.join(partial_names)} is below the expected proficiency level."
        )
    elif missing_names:
        narrative_parts.append(
            f"However, {', '.join(missing_names)} is missing from your profile."
        )

    if prioritized_gaps:
        top_focus = prioritized_gaps[0].get("name", "key skills")
        narrative_parts.append(
            f"Prioritizing {top_focus} will yield the highest immediate increase in your job alignment."
        )
    else:
        narrative_parts.append("You currently satisfy all listed skill requirements for this position!")

    summary_narrative = " ".join(narrative_parts)

    total_req = len(matched_skills) + len(partial_gaps) + len(missing_skills)
    score_mechanics = (
        f"Your alignment score of {match_score}% is computed across {total_req} required skills. "
        f"Each skill contributes up to 100% based on the ratio min(student_level / required_level, 1.0). "
        f"The final score is the unweighted average of all required skills."
    )

    return {
        "summary": summary_narrative,
        "score_explanation": score_mechanics,
        "matched_skills_summary": matched_names,
        "partial_gaps_summary": partial_names,
        "missing_skills_summary": missing_names,
        "disclaimer": STANDARD_DISCLAIMER,
    }
