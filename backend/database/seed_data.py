"""
seed_data.py: Populates relational tables with benchmark jobs, questions, and students.
"""

from sqlalchemy.orm import Session
from backend.database.connection import SessionLocal, init_db
from backend.models.db_models import (
    Student,
    StudentSkill,
    Job,
    JobSkill,
    AssessmentQuestion,
)
from backend.services.data_service import (
    load_jobs,
    load_students,
    load_assessment_questions,
)


def seed_database(db: Session | None = None) -> None:
    """Populates database with benchmark CSV data if tables are empty."""
    init_db()
    session = db if db else SessionLocal()

    try:
        # 1. Seed Jobs
        if session.query(Job).count() == 0:
            csv_jobs = load_jobs()
            for j in csv_jobs:
                job_record = Job(
                    job_id=j["job_id"],
                    title=j["title"],
                    domain=j["domain"],
                    experience_level=j["experience_level"],
                )
                session.add(job_record)
                for s in j["job_skills"]:
                    session.add(
                        JobSkill(
                            job_id=j["job_id"],
                            skill_name=s["name"],
                            required_level=s["required_level"],
                        )
                    )
            print(f"Seeded {len(csv_jobs)} benchmark jobs.")

        # 2. Seed Students
        if session.query(Student).count() == 0:
            csv_students = load_students()
            for s in csv_students:
                student_record = Student(
                    student_id=s["student_id"],
                    name=s["name"],
                    email=s["email"],
                )
                session.add(student_record)
                for sk in s["student_skills"]:
                    session.add(
                        StudentSkill(
                            student_id=s["student_id"],
                            skill_name=sk["name"],
                            level=sk["level"],
                        )
                    )
            print(f"Seeded {len(csv_students)} student profiles.")

        # 3. Seed Assessment Questions
        if session.query(AssessmentQuestion).count() == 0:
            csv_questions = load_assessment_questions()
            for q in csv_questions:
                session.add(
                    AssessmentQuestion(
                        question_id=q["question_id"],
                        skill=q["skill"],
                        question_text=q["question_text"],
                        option_a=q["options"]["A"],
                        option_b=q["options"]["B"],
                        option_c=q["options"]["C"],
                        option_d=q["options"]["D"],
                        correct_option=q["correct_option"],
                        difficulty=q["difficulty"],
                    )
                )
            print(f"Seeded {len(csv_questions)} assessment questions.")

        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        if not db:
            session.close()


if __name__ == "__main__":
    seed_database()
