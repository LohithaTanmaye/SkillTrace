"""
test_matcher.py: Unit tests for exact, normalized, and fallback semantic skill matching.
"""

from skilltrace_ai.matcher import match_skill
from skilltrace_ai.semantic import token_similarity, find_semantic_match


def test_exact_and_normalized_matching():
    student_skills = [
        {"name": "Python", "level": 4},
        {"name": "postgresql", "level": 3},
        {"name": "react.js", "level": 3},
    ]

    # Exact match
    matched, match_type, conf = match_skill("Python", student_skills)
    assert matched is not None
    assert matched["name"] == "Python"
    assert match_type == "exact_normalized"
    assert conf == 1.0

    # Casing & whitespace variation
    matched_case, _, _ = match_skill("  python  ", student_skills)
    assert matched_case is not None
    assert matched_case["name"] == "Python"

    # Alias variation ("postgres" -> "postgresql")
    matched_alias, _, _ = match_skill("postgres", student_skills)
    assert matched_alias is not None
    assert matched_alias["name"] == "postgresql"

    # Alias variation ("react" -> "react.js")
    matched_react, _, _ = match_skill("react", student_skills)
    assert matched_react is not None
    assert matched_react["name"] == "react.js"


def test_missing_skill_matching():
    student_skills = [{"name": "Python", "level": 4}]
    matched, match_type, conf = match_skill("Docker", student_skills, enable_semantic=False)
    assert matched is None
    assert match_type == "missing"
    assert conf == 0.0


def test_semantic_fallback_graceful_handling():
    student_skills = [
        {"name": "scikit-learn", "level": 3},
        {"name": "fastapi", "level": 4},
    ]

    # Without semantic enabled, unmapped variant is missing
    m1, match_type1, _ = match_skill("sklearn machine learning", student_skills, enable_semantic=False)
    assert m1 is None

    # Deterministic token similarity check directly
    sim = token_similarity("fastapi", "fast api framework")
    assert sim > 0.4

    # With semantic enabled, graceful execution without crashing
    m2, mtype2, score2 = match_skill(
        "fastapi", student_skills, enable_semantic=True, semantic_threshold=0.70
    )
    assert m2 is not None
    assert m2["name"] == "fastapi"
