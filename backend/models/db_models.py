"""
db_models.py: SQLAlchemy 2.0 ORM models for SKILLTRACE persistence.
"""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(120), nullable=False)
    degree: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    target_role: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    training_program: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    placement_status: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    salary_lpa: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    latest_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    initial_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    improvement_delta: Mapped[Optional[float]] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    skills: Mapped[List["StudentSkill"]] = relationship(
        "StudentSkill", back_populates="student", cascade="all, delete-orphan"
    )
    match_records: Mapped[List["JobMatchRecord"]] = relationship(
        "JobMatchRecord", back_populates="student"
    )


class StudentSkill(Base):
    __tablename__ = "student_skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("students.student_id"), nullable=False, index=True
    )
    skill_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    level: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5

    student: Mapped["Student"] = relationship("Student", back_populates="skills")


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    domain: Mapped[str] = mapped_column(String(100), nullable=False)
    experience_level: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    required_skills: Mapped[List["JobSkill"]] = relationship(
        "JobSkill", back_populates="job", cascade="all, delete-orphan"
    )
    match_records: Mapped[List["JobMatchRecord"]] = relationship(
        "JobMatchRecord", back_populates="job"
    )


class JobSkill(Base):
    __tablename__ = "job_skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("jobs.job_id"), nullable=False, index=True
    )
    skill_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    required_level: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5

    job: Mapped["Job"] = relationship("Job", back_populates="required_skills")


class AssessmentQuestion(Base):
    __tablename__ = "assessment_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    skill: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    option_a: Mapped[str] = mapped_column(String(255), nullable=False)
    option_b: Mapped[str] = mapped_column(String(255), nullable=False)
    option_c: Mapped[str] = mapped_column(String(255), nullable=False)
    option_d: Mapped[str] = mapped_column(String(255), nullable=False)
    correct_option: Mapped[str] = mapped_column(String(5), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(50), nullable=False)


class AssessmentSubmission(Base):
    __tablename__ = "assessment_submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    skill: Mapped[str] = mapped_column(String(100), nullable=False)
    questions_count: Mapped[int] = mapped_column(Integer, nullable=False)
    correct_count: Mapped[int] = mapped_column(Integer, nullable=False)
    percentage: Mapped[float] = mapped_column(Float, nullable=False)
    estimated_level: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )


class JobMatchRecord(Base):
    __tablename__ = "job_match_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("students.student_id"), nullable=False, index=True
    )
    job_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("jobs.job_id"), nullable=False, index=True
    )
    match_score: Mapped[float] = mapped_column(Float, nullable=False)
    analysis_json: Mapped[str] = mapped_column(Text, nullable=False)  # JSON-stringified analysis
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    student: Mapped["Student"] = relationship("Student", back_populates="match_records")
    job: Mapped["Job"] = relationship("Job", back_populates="match_records")
