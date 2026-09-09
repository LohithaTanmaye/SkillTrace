"""
scorer.py: Interpretable, auditable match score calculation.
Formula:
  skill_score = min(student_level / required_level, 1.0)
  match_score = round(average(skill_scores) * 100, 1)
"""

from typing import Any, Dict, List


def calculate_match_score(evaluated_skills: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes transparent, explainable skill alignment score.
    Accepts list of evaluated skill dicts from gaps.py containing:
      required_level, student_level, match_ratio.
    """
    if not evaluated_skills:
        return {
            "match_score": 0.0,
            "total_required_skills": 0,
            "formula": "No required skills specified.",
            "breakdown": [],
        }

    skill_scores = []
    breakdown = []

    for item in evaluated_skills:
        req = max(1, item.get("required_level", 1))
        stu = max(0, item.get("student_level", 0))
        ratio = min(stu / req, 1.0)
        skill_scores.append(ratio)

        breakdown.append({
            "skill": item.get("name", "Unknown"),
            "student_level": stu,
            "required_level": req,
            "ratio": round(ratio, 4),
            "percentage_contribution": round(ratio * 100.0, 1),
        })

    average_ratio = sum(skill_scores) / len(skill_scores)
    overall_score = round(average_ratio * 100.0, 1)

    return {
        "match_score": overall_score,
        "total_required_skills": len(skill_scores),
        "formula": "average(min(student_level / required_level, 1.0)) * 100",
        "breakdown": breakdown,
    }
