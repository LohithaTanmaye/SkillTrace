"""
job_routes.py: API endpoints for retrieving benchmark job descriptions and skills.
"""

from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException
from backend.services.data_service import load_jobs, get_job_by_id

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("", response_model=List[Dict[str, Any]])
def list_jobs():
    """Returns all benchmark job roles and their required skill sets."""
    return load_jobs()


@router.get("/{job_id}", response_model=Dict[str, Any])
def get_job(job_id: str):
    """Retrieves a specific benchmark job role by its identifier."""
    job = get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job with ID '{job_id}' not found.")
    return job
