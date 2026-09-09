"""
test_api.py: Integration tests for FastAPI endpoints using TestClient.
"""

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_root_and_health():
    # Verify metadata endpoint
    res_meta = client.get("/api/meta")
    assert res_meta.status_code == 200
    meta_data = res_meta.json()
    assert meta_data["project"] == "SKILLTRACE"
    assert meta_data["status"] == "online"

    # Verify health check
    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"


def test_jobs_endpoints():
    res = client.get("/jobs")
    assert res.status_code == 200
    jobs = res.json()
    assert len(jobs) >= 5

    res_single = client.get("/jobs/JOB001")
    assert res_single.status_code == 200
    assert res_single.json()["title"] == "Junior Data Analyst"

    res_404 = client.get("/jobs/JOB_UNKNOWN")
    assert res_404.status_code == 404


def test_students_endpoints():
    res = client.get("/students")
    assert res.status_code == 200
    students = res.json()
    assert len(students) >= 4

    res_single = client.get("/students/STU001")
    assert res_single.status_code == 200
    assert res_single.json()["name"] == "Rahul Sharma"

    res_404 = client.get("/students/STU_UNKNOWN")
    assert res_404.status_code == 404


def test_analyze_endpoint():
    payload = {
        "job_title": "Junior Data Analyst",
        "student_skills": [
            {"name": "Python", "level": 4},
            {"name": "SQL", "level": 3},
        ],
        "job_skills": [
            {"name": "Python", "required_level": 4},
            {"name": "SQL", "required_level": 4},
            {"name": "Power BI", "required_level": 3},
        ],
    }
    res = client.post("/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["match_score"] == 58.3
    assert len(data["matched_skills"]) == 1
    assert len(data["partial_gaps"]) == 1
    assert len(data["missing_skills"]) == 1
    assert "estimate of skill alignment" in data["disclaimer"]


def test_analyze_endpoint_validation_error():
    # Missing required fields
    res = client.post("/analyze", json={"student_skills": "invalid"})
    assert res.status_code == 422


def test_match_job_endpoint():
    payload = {"student_id": "STU001", "job_id": "JOB001"}
    res = client.post("/match-job", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "match_score" in data
    assert "recommendations" in data

    # Unknown ID error
    res_unknown = client.post("/match-job", json={"student_id": "STU999", "job_id": "JOB001"})
    assert res_unknown.status_code == 404


def test_assessment_endpoints():
    # 1. Fetch questions
    res_q = client.get("/assessment/questions")
    assert res_q.status_code == 200
    questions = res_q.json()
    assert len(questions) >= 10
    # Verify correct_option is NOT leaked
    assert "correct_option" not in questions[0]

    # 2. Raw evaluation
    raw_payload = {
        "assessment": [
            {"skill": "Python", "questions": 10, "correct_answers": 8},
            {"skill": "SQL", "questions": 10, "correct_answers": 6},
        ]
    }
    res_eval = client.post("/assessment/evaluate", json=raw_payload)
    assert res_eval.status_code == 200
    eval_data = res_eval.json()["evaluated_skills"]
    assert len(eval_data) == 2
    assert eval_data[0]["estimated_level"] == 4

    # 3. Interactive submission with job matching
    submit_payload = {
        "answers": [
            {"question_id": "Q101", "selected_option": "C"}, # Python correct
            {"question_id": "Q102", "selected_option": "B"}, # Python correct
            {"question_id": "Q105", "selected_option": "B"}, # SQL correct
        ],
        "target_job_id": "JOB001"
    }
    res_submit = client.post("/assessment/submit", json=submit_payload)
    assert res_submit.status_code == 200
    submit_data = res_submit.json()
    assert "evaluated_skills" in submit_data
    assert "student_skills_profile" in submit_data
    assert submit_data["job_analysis"] is not None
    assert "match_score" in submit_data["job_analysis"]
