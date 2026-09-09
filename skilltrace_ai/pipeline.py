"""
pipeline.py: High-level end-to-end orchestration pipeline for SKILLTRACE AI.
Exposes the public APIs: analyze_student, analyze_assessment, assessment_to_student_skills.
"""

from typing import Any, Dict, List, Optional
from skilltrace_ai.assessment import (
    analyze_assessment as core_analyze_assessment,
    assessment_to_student_skills as core_assessment_to_student_skills,
)
from skilltrace_ai.explainer import generate_explanation
from skilltrace_ai.gaps import detect_skill_gaps
from skilltrace_ai.prioritizer import prioritize_skill_gaps
from skilltrace_ai.recommender import generate_recommendations
from skilltrace_ai.scorer import calculate_match_score


def analyze_assessment(assessment_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates assessment questions/answers and produces proficiency level estimates.
    """
    return core_analyze_assessment(assessment_data)


def assessment_to_student_skills(assessment_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Converts assessment evaluation output into a student skills profile.
    """
    return core_assessment_to_student_skills(assessment_results)


def analyze_student(
    payload: Dict[str, Any],
    enable_semantic: bool = False,
    semantic_threshold: float = 0.75,
) -> Dict[str, Any]:
    """
    End-to-end analysis of student skills vs target job skills.
    
    Accepts:
    {
        "student_skills": [{"name": "Python", "level": 4}, ...],
        "job_skills": [{"name": "Python", "required_level": 4}, ...]
    }

    Returns:
    {
        "match_score": 58.3,
        "matched_skills": [...],
        "skill_gaps": [...],
        "partial_gaps": [...],
        "missing_skills": [...],
        "prioritized_gaps": [...],
        "recommendations": [...],
        "explanation": "...",
        "explanation_details": {...},
        "score_breakdown": [...],
        "disclaimer": "..."
    }
    """
    if not isinstance(payload, dict):
        raise ValueError("Payload must be a dictionary.")

    student_skills = payload.get("student_skills", [])
    job_skills = payload.get("job_skills", [])
    job_title = payload.get("job_title", "target job")

    if not isinstance(student_skills, list):
        raise ValueError("'student_skills' must be a list.")
    if not isinstance(job_skills, list):
        raise ValueError("'job_skills' must be a list.")

    # 1. Detect gaps across 3 tiers (Matched, Partial Gap, Missing)
    gap_data = detect_skill_gaps(
        job_skills=job_skills,
        student_skills=student_skills,
        enable_semantic=enable_semantic,
        semantic_threshold=semantic_threshold,
    )

    # 2. Compute interpretable match score
    score_data = calculate_match_score(gap_data["all_evaluated"])

    # 3. Prioritize gaps by urgency/severity
    prioritized = prioritize_skill_gaps(gap_data["all_gaps"])

    # 4. Generate targeted, actionable learning recommendations
    recommendations = generate_recommendations(prioritized)

    # 5. Build human-readable explanation and ethical disclaimer
    explanation_data = generate_explanation(
        match_score=score_data["match_score"],
        matched_skills=gap_data["matched_skills"],
        partial_gaps=gap_data["partial_gaps"],
        missing_skills=gap_data["missing_skills"],
        prioritized_gaps=prioritized,
        job_title=job_title,
    )

    return {
        "match_score": score_data["match_score"],
        "matched_skills": gap_data["matched_skills"],
        "partial_gaps": gap_data["partial_gaps"],
        "missing_skills": gap_data["missing_skills"],
        "skill_gaps": gap_data["all_gaps"],
        "prioritized_gaps": prioritized,
        "recommendations": recommendations,
        "explanation": explanation_data["summary"],
        "explanation_details": explanation_data,
        "score_breakdown": score_data["breakdown"],
        "disclaimer": explanation_data["disclaimer"],
    }
