"""
gaps.py: 3-tier skill gap categorization:
1. Matched: Student level meets or exceeds the required level.
2. Partial Gap: Student possesses the skill, but level is below required.
3. Missing: Skill is completely absent from student profile.
"""

from typing import Any, Dict, List
from skilltrace_ai.matcher import match_skill


def detect_skill_gaps(
    job_skills: List[Dict[str, Any]],
    student_skills: List[Dict[str, Any]],
    enable_semantic: bool = False,
    semantic_threshold: float = 0.75,
) -> Dict[str, Any]:
    """
    Evaluates every required job skill against student capabilities.
    Categorizes skills into matched_skills, partial_gaps, and missing_skills.
    """
    matched_skills = []
    partial_gaps = []
    missing_skills = []
    all_evaluated = []

    for job_skill in job_skills:
        skill_name = job_skill.get("name", "").strip()
        if not skill_name:
            continue

        try:
            req_level = int(job_skill.get("required_level", 1))
        except (ValueError, TypeError):
            req_level = 1
        req_level = max(1, min(5, req_level))

        # Attempt to match against student profile
        student_match, match_type, confidence = match_skill(
            required_skill_name=skill_name,
            student_skills=student_skills,
            enable_semantic=enable_semantic,
            semantic_threshold=semantic_threshold,
        )

        if student_match is not None:
            try:
                stu_level = int(student_match.get("level", 0))
            except (ValueError, TypeError):
                stu_level = 0
            stu_level = max(0, min(5, stu_level))
        else:
            stu_level = 0

        deficit = max(0, req_level - stu_level)
        ratio = round(min(stu_level / req_level, 1.0), 3) if req_level > 0 else 1.0

        item = {
            "name": skill_name,
            "required_level": req_level,
            "student_level": stu_level,
            "deficit": deficit,
            "match_ratio": ratio,
            "match_type": match_type,
            "confidence": confidence,
        }

        all_evaluated.append(item)

        if stu_level == 0:
            item["category"] = "missing"
            missing_skills.append(item)
        elif stu_level < req_level:
            item["category"] = "partial_gap"
            partial_gaps.append(item)
        else:
            item["category"] = "matched"
            matched_skills.append(item)

    all_gaps = partial_gaps + missing_skills

    return {
        "matched_skills": matched_skills,
        "partial_gaps": partial_gaps,
        "missing_skills": missing_skills,
        "all_gaps": all_gaps,
        "all_evaluated": all_evaluated,
    }
