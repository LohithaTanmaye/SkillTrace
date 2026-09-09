"""
test_full_integration.py: End-to-end integration test verifying the connected system:
Frontend static mounting, Assessment Submission, AI Pipeline, and Results generation.
"""

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_frontend_static_serving():
    # 1. Landing page
    res_index = client.get("/")
    assert res_index.status_code == 200
    assert "SKILLTRACE" in res_index.text
    assert "<title>" in res_index.text

    # 2. Assessment page
    res_assess = client.get("/assessment.html")
    assert res_assess.status_code == 200
    assert "Pre-Assessment" in res_assess.text

    # 3. Dashboard page
    res_dash = client.get("/dashboard.html")
    assert res_dash.status_code == 200
    assert "Student Skill Profile" in res_dash.text

    # 4. Results page
    res_res = client.get("/results.html")
    assert res_res.status_code == 200
    assert "Job Readiness" in res_res.text


def test_complete_end_to_end_user_journey():
    # 1. Client loads benchmark jobs to choose target role
    jobs_res = client.get("/jobs")
    assert jobs_res.status_code == 200
    jobs = jobs_res.json()
    assert len(jobs) >= 5

    # 2. Student takes pre-assessment
    questions_res = client.get("/assessment/questions")
    assert questions_res.status_code == 200
    questions = questions_res.json()
    assert len(questions) >= 10

    # 3. Student answers questions: 2 Python correct, 1 SQL correct
    # Q101 correct is C, Q102 correct is B, Q105 correct is B
    submission_payload = {
        "answers": [
            {"question_id": "Q101", "selected_option": "C"},
            {"question_id": "Q102", "selected_option": "B"},
            {"question_id": "Q105", "selected_option": "B"},
        ],
        "target_job_id": "JOB001",  # Junior Data Analyst
    }

    submit_res = client.post("/assessment/submit", json=submission_payload)
    assert submit_res.status_code == 200
    data = submit_res.json()

    # Verify assessment evaluation
    assert "evaluated_skills" in data
    assert "student_skills_profile" in data
    profile = {s["name"]: s["level"] for s in data["student_skills_profile"]}
    assert "Python" in profile
    assert "SQL" in profile

    # Verify immediate job readiness analysis
    job_analysis = data["job_analysis"]
    assert job_analysis is not None
    assert "match_score" in job_analysis
    assert isinstance(job_analysis["match_score"], (int, float))
    assert len(job_analysis["matched_skills"]) > 0 or len(job_analysis["skill_gaps"]) > 0
    assert len(job_analysis["recommendations"]) > 0
    assert "disclaimer" in job_analysis
    assert "does not guarantee job suitability or employment" in job_analysis["disclaimer"]
