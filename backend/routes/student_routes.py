"""
student_routes.py: API endpoints for accessing student profiles and skills.
"""

from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException
from backend.services.data_service import load_students, get_student_by_id

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
