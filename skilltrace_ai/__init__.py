"""
skilltrace_ai: Core intelligence library for SKILLTRACE.
Provides deterministic, explainable skill matching, gap identification,
assessment mapping, auditable scoring, prioritization, and recommendations.
"""

from skilltrace_ai.pipeline import (
    analyze_student,
    analyze_assessment,
    assessment_to_student_skills,
)

__all__ = [
    "analyze_student",
    "analyze_assessment",
    "assessment_to_student_skills",
]
