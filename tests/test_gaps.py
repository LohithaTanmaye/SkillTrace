"""
test_gaps.py: Unit tests for 3-tier skill gap identification.
Tiers:
  - Matched: student_level >= required_level
  - Partial Gap: 0 < student_level < required_level
  - Missing: student_level == 0 (not in profile)
"""

from skilltrace_ai.gaps import detect_skill_gaps


def test_gap_detection_three_tiers():
    job_skills = [
        {"name": "Python", "required_level": 4},
        {"name": "SQL", "required_level": 4},
        {"name": "Power BI", "required_level": 3},
    ]

    student_skills = [
        {"name": "Python", "level": 4},  # Meets requirement -> Matched
        {"name": "SQL", "level": 2},     # Deficit 2 -> Partial Gap
        # Power BI missing -> Missing
    ]

    result = detect_skill_gaps(job_skills, student_skills)

    matched = result["matched_skills"]
    partial = result["partial_gaps"]
    missing = result["missing_skills"]

    assert len(matched) == 1
    assert matched[0]["name"] == "Python"
    assert matched[0]["category"] == "matched"
    assert matched[0]["deficit"] == 0

    assert len(partial) == 1
    assert partial[0]["name"] == "SQL"
    assert partial[0]["category"] == "partial_gap"
    assert partial[0]["deficit"] == 2

    assert len(missing) == 1
    assert missing[0]["name"] == "Power BI"
    assert missing[0]["category"] == "missing"
    assert missing[0]["deficit"] == 3


def test_student_level_exceeds_requirement():
    job_skills = [{"name": "Python", "required_level": 3}]
    student_skills = [{"name": "Python", "level": 5}]

    result = detect_skill_gaps(job_skills, student_skills)
    assert len(result["matched_skills"]) == 1
    assert result["matched_skills"][0]["match_ratio"] == 1.0
    assert result["matched_skills"][0]["deficit"] == 0


def test_empty_skill_lists():
    # Empty student skills -> all required skills are missing
    job_skills = [{"name": "Python", "required_level": 4}]
    res_no_student = detect_skill_gaps(job_skills, [])
    assert len(res_no_student["missing_skills"]) == 1

    # Empty job skills -> all lists empty
    res_no_job = detect_skill_gaps([], [{"name": "Python", "level": 4}])
    assert len(res_no_job["matched_skills"]) == 0
    assert len(res_no_job["all_gaps"]) == 0


def test_invalid_level_types_graceful_handling():
    job_skills = [{"name": "Python", "required_level": "four"}]  # Non-integer
    student_skills = [{"name": "Python", "level": None}]         # None

    result = detect_skill_gaps(job_skills, student_skills)
    assert len(result["all_evaluated"]) == 1
    assert result["all_evaluated"][0]["required_level"] == 1
