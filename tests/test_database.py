"""
test_database.py: Unit and integration tests for SQLAlchemy database models and operations.
Uses an isolated in-memory SQLite engine to verify schemas and relationships without disk writes.
"""

import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.db_models import (
    Base,
    Student,
    StudentSkill,
    Job,
    JobSkill,
    AssessmentQuestion,
    AssessmentSubmission,
    JobMatchRecord,
)
from backend.database.seed_data import seed_database


def test_database_tables_and_relationships():
    # Setup test in-memory engine
    test_engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=test_engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSession()

    try:
        # Create a student with skills
        stu = Student(
            student_id="STU_TEST",
            name="Test User",
            email="test@example.com",
        )
        session.add(stu)
        session.flush()

        skill1 = StudentSkill(student_id="STU_TEST", skill_name="Python", level=4)
        skill2 = StudentSkill(student_id="STU_TEST", skill_name="SQL", level=3)
        session.add_all([skill1, skill2])
        session.commit()

        # Query and verify relations
        queried_stu = session.query(Student).filter_by(student_id="STU_TEST").first()
        assert queried_stu is not None
        assert queried_stu.name == "Test User"
        assert len(queried_stu.skills) == 2
        skill_names = [s.skill_name for s in queried_stu.skills]
        assert "Python" in skill_names
        assert "SQL" in skill_names

        # Create a job with required skills
        job = Job(
            job_id="JOB_TEST",
            title="Junior Data Analyst",
            domain="Data Science",
            experience_level="Entry",
        )
        session.add(job)
        session.flush()

        js1 = JobSkill(job_id="JOB_TEST", skill_name="Python", required_level=4)
        js2 = JobSkill(job_id="JOB_TEST", skill_name="SQL", required_level=4)
        js3 = JobSkill(job_id="JOB_TEST", skill_name="Power BI", required_level=3)
        session.add_all([js1, js2, js3])
        session.commit()

        queried_job = session.query(Job).filter_by(job_id="JOB_TEST").first()
        assert queried_job is not None
        assert len(queried_job.required_skills) == 3

        # Record assessment submission
        sub = AssessmentSubmission(
            student_id="STU_TEST",
            skill="Python",
            questions_count=10,
            correct_count=8,
            percentage=80.0,
            estimated_level=4,
        )
        session.add(sub)
        session.commit()

        queried_sub = session.query(AssessmentSubmission).filter_by(student_id="STU_TEST").first()
        assert queried_sub is not None
        assert queried_sub.estimated_level == 4

        # Record job match
        analysis_data = {"match_score": 58.3, "matched_skills": ["Python"]}
        match_rec = JobMatchRecord(
            student_id="STU_TEST",
            job_id="JOB_TEST",
            match_score=58.3,
            analysis_json=json.dumps(analysis_data),
        )
        session.add(match_rec)
        session.commit()

        queried_match = session.query(JobMatchRecord).filter_by(student_id="STU_TEST").first()
        assert queried_match is not None
        assert queried_match.match_score == 58.3
        parsed = json.loads(queried_match.analysis_json)
        assert parsed["match_score"] == 58.3
    finally:
        session.close()


def test_seed_database_execution():
    test_engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=test_engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSession()

    try:
        # Run seed
        seed_database(session)

        # Assert data exists
        assert session.query(Job).count() >= 5
        assert session.query(Student).count() >= 4
        assert session.query(AssessmentQuestion).count() >= 10
    finally:
        session.close()
