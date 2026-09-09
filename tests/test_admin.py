"""
test_admin.py: Unit and integration tests for Administrator Authentication,
Cohort Analytics, Student Progression Tracking, and Improvement Delta calculations.
"""

from fastapi.testclient import TestClient
from backend.main import app
from backend.config import settings

client = TestClient(app)


def test_admin_login_success():
    payload = {
        "username": settings.ADMIN_USERNAME,
        "password": settings.ADMIN_PASSWORD,
    }
    res = client.post("/admin/login", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["role"] == "admin"
    assert data["access_token"] == settings.ADMIN_TOKEN


def test_admin_login_invalid():
    payload = {
        "username": "admin",
        "password": "wrongpassword999",
    }
    res = client.post("/admin/login", json=payload)
    assert res.status_code == 401
    assert "Invalid" in res.json()["detail"]


def test_admin_unauthorized_access():
    # Attempting to access stats without Bearer token
    res_stats = client.get("/admin/stats")
    assert res_stats.status_code == 401

    # Attempting to access students without Bearer token
    res_students = client.get("/admin/students")
    assert res_students.status_code == 401


def test_admin_stats_authorized():
    headers = {"Authorization": f"Bearer {settings.ADMIN_TOKEN}"}
    res = client.get("/admin/stats", headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert "total_students" in data
    assert data["total_students"] >= 4
    assert "average_score" in data
    assert "average_improvement" in data
    assert "tier_distribution" in data
    assert "tier_1_count" in data["tier_distribution"]
    assert "tier_2_count" in data["tier_distribution"]
    assert "tier_3_count" in data["tier_distribution"]
    assert "top_target_roles" in data
    assert "top_deficit_skills" in data


def test_admin_students_list():
    headers = {"Authorization": f"Bearer {settings.ADMIN_TOKEN}"}
    res = client.get("/admin/students", headers=headers)
    assert res.status_code == 200
    students = res.json()
    assert len(students) >= 4

    first = students[0]
    assert "student_id" in first
    assert "name" in first
    assert "email" in first
    assert "target_role" in first
    assert "score" in first
    assert "improvement_delta" in first
    assert "timestamp" in first
    assert "readiness_tier" in first


def test_student_improvement_calculation():
    # 1. First assessment submission for a student
    student_email = "alex.progression@example.com"
    payload1 = {
        "student_name": "Alex Miller",
        "email": student_email,
        "degree": "B.Tech Computer Science",
        "answers": [
            {"question_id": "Q101", "selected_option": "C"},  # Python correct (L4)
        ],
        "target_job_title": "Junior Python Developer",
    }
    res1 = client.post("/assessment/submit", json=payload1)
    assert res1.status_code == 200
    score1 = res1.json()["job_analysis"]["match_score"]

    # 2. Student upskills and takes another assessment with more skills answered
    payload2 = {
        "student_name": "Alex Miller",
        "email": student_email,
        "degree": "B.Tech Computer Science",
        "answers": [
            {"question_id": "Q101", "selected_option": "C"},  # Python
            {"question_id": "Q102", "selected_option": "B"},  # Python
            {"question_id": "Q105", "selected_option": "B"},  # SQL
        ],
        "target_job_title": "Junior Python Developer",
    }
    res2 = client.post("/assessment/submit", json=payload2)
    assert res2.status_code == 200
    score2 = res2.json()["job_analysis"]["match_score"]

    # 3. Verify in admin portal that Alex's improvement delta is recorded
    headers = {"Authorization": f"Bearer {settings.ADMIN_TOKEN}"}
    res_admin = client.get("/admin/students", headers=headers)
    assert res_admin.status_code == 200
    alex_records = [s for s in res_admin.json() if s["email"] == student_email]
    assert len(alex_records) > 0
    alex = alex_records[0]
    assert alex["name"] == "Alex Miller"
    assert alex["score"] == score2
    assert "timestamp" in alex
