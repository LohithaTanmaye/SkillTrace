"""
test_new_features.py: Verification of New Student Registration, Level-by-Level Roadmaps,
and Multi-Role Career Recommendations ("Inka em em roles ki apply cheyochu").
"""

from fastapi.testclient import TestClient
from backend.main import app
from skilltrace_ai.recommender import get_level_milestones, generate_recommendations

client = TestClient(app)


def test_register_new_student():
    payload = {
        "name": "Lohitha Tanmaye",
        "email": "lohita.test@example.com",
        "degree": "B.Tech AI & Data Science",
        "student_skills": [
            {"name": "Python", "level": 4},
            {"name": "FastAPI", "level": 3},
            {"name": "SQL", "level": 3},
        ],
    }

    res = client.post("/students", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert "student_id" in data
    assert data["name"] == "Lohitha Tanmaye"
    assert len(data["student_skills"]) == 3

    # Verify student is in list
    res_list = client.get("/students")
    assert res_list.status_code == 200
    student_ids = [s["student_id"] for s in res_list.json()]
    assert data["student_id"] in student_ids


def test_multi_role_career_matching():
    # Student with strong Python & SQL skills
    student_skills = [
        {"name": "Python", "level": 4},
        {"name": "SQL", "level": 4},
        {"name": "Excel", "level": 4},
    ]

    res = client.post("/analyze/all-roles", json=student_skills)
    assert res.status_code == 200
    data = res.json()

    assert "ranked_roles" in data
    assert data["total_roles_evaluated"] >= 5
    assert data["best_fit_role"] is not None

    ranked = data["ranked_roles"]
    # Check descending order by score
    scores = [r["match_score"] for r in ranked]
    assert scores == sorted(scores, reverse=True)

    # Check fit tiers
    for role in ranked:
        assert role["fit_tier"] in ["Ready to Apply", "Close Match", "Future Target"]
        assert "matched_skill_names" in role
        assert "top_missing_skills" in role


def test_level_by_level_study_roadmap():
    # Missing Power BI required at level 3
    prioritized_gaps = [
        {
            "rank": 1,
            "name": "Power BI",
            "required_level": 3,
            "student_level": 0,
            "urgency": "HIGH",
        }
    ]

    recs = generate_recommendations(prioritized_gaps)
    assert len(recs) == 1
    pbi_rec = recs[0]
    assert "level_roadmap" in pbi_rec
    roadmap = pbi_rec["level_roadmap"]
    assert len(roadmap) >= 1

    # Verify each milestone has focus topics and suggested project
    for m in roadmap:
        assert "title" in m
        assert "focus_topics" in m
        assert "suggested_project" in m
        assert len(m["suggested_project"]) > 5
