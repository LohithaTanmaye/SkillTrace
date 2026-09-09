"""
matcher.py: Exact, normalized, and optional semantic skill matching.
"""

from typing import Any, Dict, List, Optional, Tuple
from skilltrace_ai.normalization import normalize_skill_name
from skilltrace_ai.semantic import find_semantic_match


def match_skill(
    required_skill_name: str,
    student_skills: List[Dict[str, Any]],
    enable_semantic: bool = False,
    semantic_threshold: float = 0.75,
) -> Tuple[Optional[Dict[str, Any]], str, float]:
    """
    Attempts to match a required skill against a student's skills profile.
    Priority 1: Exact or normalized canonical match (100% deterministic).
    Priority 2: Semantic embedding / token similarity (if enable_semantic is True).
    Returns: (matched_student_skill_dict_or_None, match_type, confidence)
    """
    if not required_skill_name or not student_skills:
        return None, "missing", 0.0

    target_norm = normalize_skill_name(required_skill_name)

    # 1. Exact or normalized matching
    for skill in student_skills:
        cand_norm = normalize_skill_name(skill.get("name", ""))
        if target_norm == cand_norm:
            return skill, "exact_normalized", 1.0

    # 2. Semantic matching (optional)
    if enable_semantic:
        matched, score, method = find_semantic_match(
            target_skill=required_skill_name,
            candidate_skills=student_skills,
            threshold=semantic_threshold,
        )
        if matched and score >= semantic_threshold:
            return matched, f"semantic_{method}", score

    return None, "missing", 0.0
