"""
student_routes.py: API endpoints for accessing student profiles and registering new students.
"""

from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException, status
from backend.schemas.skill_schemas import CreateStudentRequest
from backend.services.data_service import (
    load_students,
    get_student_by_id,
    add_student,
)

router = APIRouter(prefix="/students", tags=["Students"])


@router.get("", response_model=List[Dict[str, Any]])
def list_students():
    """Returns all sample student profiles."""
    return load_students()


@router.get("/{student_id}", response_model=Dict[str, Any])
def get_student(student_id: str):
    """Retrieves a specific student profile by their identifier."""
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail=f"Student with ID '{student_id}' not found.")
    return student


@router.post("", status_code=status.HTTP_201_CREATED, response_model=Dict[str, Any])
def register_student(payload: CreateStudentRequest):
    """
    Registers a new student profile and persists it to database and CSV.
    """
    try:
        skills_dict = [s.model_dump() for s in payload.student_skills]
        new_student = add_student(
            name=payload.name,
            email=payload.email,
            student_skills=skills_dict,
        )
        return new_student
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
