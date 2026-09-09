"""
assessment.py: Pre-assessment evaluation and proficiency level estimation.
Maps percentage scores to levels 1-5 based on strict inclusive upper boundaries:
0-20%   -> Level 1 (Beginner)
>20-40% -> Level 2 (Basic)
>40-60% -> Level 3 (Intermediate)
>60-80% -> Level 4 (Advanced)
>80-100%-> Level 5 (Proficient)
"""

from typing import Any, Dict, List, Tuple

PROFICIENCY_LABELS = {
    1: "Beginner",
    2: "Basic",
    3: "Intermediate",
    4: "Advanced",
    5: "Proficient",
}


def percentage_to_level(percentage: float) -> Tuple[int, str]:
    """
    Maps an assessment percentage to a skill level (1-5) and label.
    Upper boundaries are strictly inclusive:
    20.0% -> Level 1
    40.0% -> Level 2
    60.0% -> Level 3
    80.0% -> Level 4
    100.0% -> Level 5
    """
    pct = round(float(percentage), 1)

    if pct < 0.0:
        pct = 0.0
    elif pct > 100.0:
        pct = 100.0

    if pct <= 20.0:
        level = 1
    elif pct <= 40.0:
        level = 2
    elif pct <= 60.0:
        level = 3
    elif pct <= 80.0:
        level = 4
    else:
        level = 5

    return level, PROFICIENCY_LABELS[level]


def analyze_assessment(assessment_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates assessment responses and estimates skill proficiencies.
    Accepts:
    {
        "assessment": [
            {"skill": "Python", "questions": 10, "correct_answers": 8},
            ...
        ]
    }
    """
    items = assessment_data.get("assessment", [])
    if not isinstance(items, list):
        raise ValueError("Assessment data must contain an 'assessment' list.")

    evaluated_skills = []

    for item in items:
        skill = str(item.get("skill", "")).strip()
        if not skill:
            continue

        questions = int(item.get("questions", 0))
        correct = int(item.get("correct_answers", 0))

        if questions <= 0:
            raise ValueError(f"Questions count for skill '{skill}' must be greater than 0.")
        if correct < 0:
            raise ValueError(f"Correct answers count for skill '{skill}' cannot be negative.")
        if correct > questions:
            raise ValueError(
                f"Correct answers ({correct}) cannot exceed total questions ({questions}) for '{skill}'."
            )

        percentage = round((correct / questions) * 100.0, 1)
        level, label = percentage_to_level(percentage)

        evaluated_skills.append({
            "skill": skill,
            "questions": questions,
            "correct_answers": correct,
            "percentage": percentage,
            "estimated_level": level,
            "proficiency_label": label,
        })

    return {
        "evaluated_skills": evaluated_skills,
        "note": "Proficiency levels are estimates based on pre-assessment performance.",
    }


def assessment_to_student_skills(assessment_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Transforms analyzed assessment items into standard student skill profile format:
    [
        {"name": "Python", "level": 4},
        {"name": "SQL", "level": 3},
        {"name": "Power BI", "level": 1}
    ]
    """
    student_skills = []
    for item in assessment_results:
        # Handles both direct analyze_assessment output and raw assessment list
        skill_name = item.get("skill") or item.get("name")
        if not skill_name:
            continue

        if "estimated_level" in item:
            level = item["estimated_level"]
        elif "level" in item:
            level = item["level"]
        elif "questions" in item and "correct_answers" in item:
            q = int(item["questions"])
            c = int(item["correct_answers"])
            pct = (c / q * 100.0) if q > 0 else 0.0
            level, _ = percentage_to_level(pct)
        else:
            level = 1

        student_skills.append({
            "name": skill_name.strip(),
            "level": int(level),
        })

    return student_skills
