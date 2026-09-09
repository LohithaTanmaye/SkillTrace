"""
data_service.py: Data transformation layer for CSV inputs in SKILLTRACE.
Responsible for reading, writing, and transforming records into structured Python dicts.
"""

from __future__ import annotations
import csv
from pathlib import Path
from typing import Any, Dict, List, Optional

# Default paths relative to project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_DATA_DIR = BASE_DIR / "data"


def parse_skills_string(skills_str: str, key_name: str = "level") -> List[Dict[str, Any]]:
    """
    Parses delimited skill strings like 'Python:4|SQL:3|Excel:4' into
    structured skill dictionaries: [{'name': 'Python', key_name: 4}, ...].
    """
    if not skills_str or not skills_str.strip():
        return []

    parsed_skills: List[Dict[str, Any]] = []
    skill_items = [s.strip() for s in skills_str.split("|") if s.strip()]

    for item in skill_items:
        if ":" in item:
            parts = item.split(":", 1)
            name = parts[0].strip()
            try:
                level = int(parts[1].strip())
            except ValueError:
                level = 1
        else:
            name = item.strip()
            level = 1

        if name:
            parsed_skills.append({"name": name, key_name: level})

    return parsed_skills


def serialize_skills_list(skills: List[Dict[str, Any]], key_name: str = "level") -> str:
    """
    Converts list of skill dicts [{'name': 'Python', 'level': 4}, ...]
    into CSV string format 'Python:4|SQL:3'.
    """
    items = []
    for s in skills:
        name = s.get("name", "").strip()
        lvl = s.get(key_name) or s.get("level") or 1
        if name:
            items.append(f"{name}:{lvl}")
    return "|".join(items)


def load_jobs(csv_path: Optional[Path | str] = None) -> List[Dict[str, Any]]:
    """Loads all benchmark job profiles from CSV."""
    path = Path(csv_path) if csv_path else DEFAULT_DATA_DIR / "jobs.csv"
    if not path.exists():
        raise FileNotFoundError(f"Jobs CSV not found at: {path}")

    jobs: List[Dict[str, Any]] = []
    with open(path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            job = {
                "job_id": row.get("job_id", "").strip(),
                "title": row.get("title", "").strip(),
                "domain": row.get("domain", "").strip(),
                "experience_level": row.get("experience_level", "").strip(),
                "job_skills": parse_skills_string(
                    row.get("skills", ""), key_name="required_level"
                ),
            }
            jobs.append(job)
    return jobs


def get_job_by_id(job_id: str, csv_path: Optional[Path | str] = None) -> Optional[Dict[str, Any]]:
    """Finds a job by its unique identifier."""
    jobs = load_jobs(csv_path)
    for job in jobs:
        if job["job_id"].lower() == job_id.lower().strip():
            return job
    return None


def load_students(csv_path: Optional[Path | str] = None) -> List[Dict[str, Any]]:
    """Loads all sample student records from CSV."""
    path = Path(csv_path) if csv_path else DEFAULT_DATA_DIR / "students.csv"
    if not path.exists():
        raise FileNotFoundError(f"Students CSV not found at: {path}")

    students: List[Dict[str, Any]] = []
    with open(path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            student = {
                "student_id": row.get("student_id", "").strip(),
                "name": row.get("name", "").strip(),
                "email": row.get("email", "").strip(),
                "student_skills": parse_skills_string(
                    row.get("skills", ""), key_name="level"
                ),
            }
            students.append(student)
    return students


def get_student_by_id(student_id: str, csv_path: Optional[Path | str] = None) -> Optional[Dict[str, Any]]:
    """Finds a student by their unique identifier."""
    students = load_students(csv_path)
    for student in students:
        if student["student_id"].lower() == student_id.lower().strip():
            return student
    return None


def add_student(
    name: str,
    email: str,
    student_skills: List[Dict[str, Any]],
    csv_path: Optional[Path | str] = None,
) -> Dict[str, Any]:
    """
    Registers a new student profile, assigns a unique ID,
    persists the record to CSV, and mirrors to database if active.
    """
    path = Path(csv_path) if csv_path else DEFAULT_DATA_DIR / "students.csv"
    existing_students = load_students(path)

    # Generate sequential ID (e.g. STU005)
    max_num = 0
    for s in existing_students:
        s_id = s.get("student_id", "")
        if s_id.startswith("STU"):
            try:
                num = int(s_id.replace("STU", ""))
                if num > max_num:
                    max_num = num
            except ValueError:
                pass

    new_id = f"STU{max_num + 1:03d}"
    skills_serialized = serialize_skills_list(student_skills, key_name="level")

    # 1. Append to CSV
    with open(path, mode="a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([new_id, name.strip(), email.strip(), skills_serialized])

    # 2. Mirror into database if connection available
    try:
        from backend.database.connection import SessionLocal
        from backend.models.db_models import Student, StudentSkill
        session = SessionLocal()
        try:
            db_student = Student(student_id=new_id, name=name.strip(), email=email.strip())
            session.add(db_student)
            for sk in student_skills:
                session.add(StudentSkill(
                    student_id=new_id,
                    skill_name=sk.get("name", "").strip(),
                    level=int(sk.get("level", 1)),
                ))
            session.commit()
        except Exception:
            session.rollback()
        finally:
            session.close()
    except Exception:
        pass

    return {
        "student_id": new_id,
        "name": name.strip(),
        "email": email.strip(),
        "student_skills": student_skills,
    }


def load_assessment_questions(
    skill: Optional[str] = None, csv_path: Optional[Path | str] = None
) -> List[Dict[str, Any]]:
    """Loads assessment questions, optionally filtered by a specific skill."""
    path = Path(csv_path) if csv_path else DEFAULT_DATA_DIR / "assessments.csv"
    if not path.exists():
        raise FileNotFoundError(f"Assessments CSV not found at: {path}")

    questions: List[Dict[str, Any]] = []
    with open(path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            question_skill = row.get("skill", "").strip()
            if skill and question_skill.lower() != skill.lower().strip():
                continue

            questions.append({
                "question_id": row.get("question_id", "").strip(),
                "skill": question_skill,
                "question_text": row.get("question_text", "").strip(),
                "options": {
                    "A": row.get("option_a", "").strip(),
                    "B": row.get("option_b", "").strip(),
                    "C": row.get("option_c", "").strip(),
                    "D": row.get("option_d", "").strip(),
                },
                "correct_option": row.get("correct_option", "").strip(),
                "difficulty": row.get("difficulty", "").strip(),
            })
    return questions


def prepare_analysis_payload(
    student_id: str, job_id: str, csv_dir: Optional[Path | str] = None
) -> Dict[str, Any]:
    """
    Transforms student and job CSV records into the exact dictionary
    structure required by skilltrace_ai.analyze_student().
    """
    data_dir = Path(csv_dir) if csv_dir else DEFAULT_DATA_DIR
    student = get_student_by_id(student_id, data_dir / "students.csv")
    if not student:
        raise ValueError(f"Student with ID '{student_id}' not found.")

    job = get_job_by_id(job_id, data_dir / "jobs.csv")
    if not job:
        raise ValueError(f"Job with ID '{job_id}' not found.")

    return {
        "student_id": student["student_id"],
        "student_name": student["name"],
        "job_id": job["job_id"],
        "job_title": job["title"],
        "student_skills": student["student_skills"],
        "job_skills": job["job_skills"],
    }
