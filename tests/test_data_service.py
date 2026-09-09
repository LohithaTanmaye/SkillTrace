"""
test_data_service.py: Automated tests for Phase 2 data service and CSV processing.
"""

import pytest
from backend.services.data_service import (
    parse_skills_string,
    load_jobs,
    get_job_by_id,
    load_students,
    get_student_by_id,
    load_assessment_questions,
    prepare_analysis_payload,
)


def test_parse_skills_string_standard():
    skills_str = "Python:4|SQL:3|Excel:4"
    result = parse_skills_string(skills_str, key_name="level")
    assert len(result) == 3
    assert result[0] == {"name": "Python", "level": 4}
    assert result[1] == {"name": "SQL", "level": 3}
    assert result[2] == {"name": "Excel", "level": 4}


def test_parse_skills_string_required_level_key():
    skills_str = "Python:4|SQL:4|Power BI:3"
    result = parse_skills_string(skills_str, key_name="required_level")
    assert len(result) == 3
    assert result[2] == {"name": "Power BI", "required_level": 3}


def test_parse_skills_string_edge_cases():
    # Empty string
    assert parse_skills_string("") == []
    assert parse_skills_string("   ") == []

    # Missing level default fallback
    result_no_level = parse_skills_string("Python|SQL:2")
    assert result_no_level[0] == {"name": "Python", "level": 1}
    assert result_no_level[1] == {"name": "SQL", "level": 2}

    # Malformed non-integer level
    result_bad_level = parse_skills_string("Python:advanced|SQL:3")
    assert result_bad_level[0] == {"name": "Python", "level": 1}
    assert result_bad_level[1] == {"name": "SQL", "level": 3}


def test_load_jobs():
    jobs = load_jobs()
    assert len(jobs) >= 5
    job_ids = [j["job_id"] for j in jobs]
    assert "JOB001" in job_ids

    analyst = next(j for j in jobs if j["job_id"] == "JOB001")
    assert analyst["title"] == "Junior Data Analyst"
    assert len(analyst["job_skills"]) >= 4
    skill_names = [s["name"] for s in analyst["job_skills"]]
    assert "Python" in skill_names
    assert "SQL" in skill_names
    assert "Power BI" in skill_names


def test_get_job_by_id():
    job = get_job_by_id("JOB001")
    assert job is not None
    assert job["title"] == "Junior Data Analyst"

    # Case-insensitive lookup test
    job_lower = get_job_by_id("job001")
    assert job_lower is not None

    # Unknown ID
    assert get_job_by_id("JOB999") is None


def test_load_students():
    students = load_students()
    assert len(students) >= 300
    rahul = next(s for s in students if s["student_id"] == "STU001")
    assert rahul["name"] == "Rahul Sharma"
    skills = {s["name"]: s["level"] for s in rahul["student_skills"]}
    assert skills.get("Python") == 4
    assert skills.get("SQL") == 3
    assert skills.get("Excel") == 4


def test_get_student_by_id():
    student = get_student_by_id("STU001")
    assert student is not None
    assert student["name"] == "Rahul Sharma"
    assert get_student_by_id("STU999") is None


def test_load_assessment_questions():
    all_questions = load_assessment_questions()
    assert len(all_questions) >= 10

    python_questions = load_assessment_questions(skill="Python")
    assert len(python_questions) >= 3
    for q in python_questions:
        assert q["skill"] == "Python"
        assert "A" in q["options"]
        assert q["correct_option"] in ["A", "B", "C", "D"]


def test_prepare_analysis_payload():
    payload = prepare_analysis_payload(student_id="STU001", job_id="JOB001")
    assert payload["student_id"] == "STU001"
    assert payload["job_id"] == "JOB001"
    assert "student_skills" in payload
    assert "job_skills" in payload
    assert isinstance(payload["student_skills"], list)
    assert isinstance(payload["job_skills"], list)

    with pytest.raises(ValueError):
        prepare_analysis_payload(student_id="STU999", job_id="JOB001")

    with pytest.raises(ValueError):
        prepare_analysis_payload(student_id="STU001", job_id="JOB999")
