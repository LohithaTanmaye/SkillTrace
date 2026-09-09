"""
test_recommender.py: Unit tests for dynamic, gap-specific recommendation generation.
"""

from skilltrace_ai.recommender import generate_recommendations


def test_recommendation_content_matches_requirements():
    prioritized_gaps = [
        {
            "rank": 1,
            "name": "Power BI",
            "required_level": 3,
            "student_level": 0,
            "urgency": "HIGH",
        },
        {
            "rank": 2,
            "name": "SQL",
            "required_level": 4,
            "student_level": 2,
            "urgency": "MEDIUM",
        },
    ]

    recs = generate_recommendations(prioritized_gaps)
    assert len(recs) == 2

    # Power BI missing recommendation
    pbi_rec = recs[0]
    assert pbi_rec["skill"] == "Power BI"
    assert "fundamentals" in pbi_rec["action"].lower()
    assert "dax" in pbi_rec["action"].lower() or "dashboards" in pbi_rec["action"].lower()

    # SQL partial gap recommendation
    sql_rec = recs[1]
    assert sql_rec["skill"] == "SQL"
    assert "level 2" in sql_rec["action"].lower()
    assert "level 4" in sql_rec["action"].lower()
    assert "joins" in sql_rec["action"].lower() or "queries" in sql_rec["action"].lower()


def test_empty_gaps_yields_empty_recommendations():
    assert generate_recommendations([]) == []
