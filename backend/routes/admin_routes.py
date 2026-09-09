"""
admin_routes.py: API endpoints for Administrator Authentication, Cohort Analytics,
and Student Progression Tracking with timestamps and improvement deltas.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from backend.config import settings
from backend.services.data_service import (
    get_admin_cohort_stats,
    get_admin_student_records,
)

router = APIRouter(prefix="/admin", tags=["Administrator"])
security = HTTPBearer(auto_error=False)


class AdminLoginRequest(BaseModel):
    username: str = Field(..., description="Administrator username")
    password: str = Field(..., description="Administrator password")


def require_admin_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> bool:
    """Validates administrator bearer token."""
    if not credentials or credentials.credentials.strip() != settings.ADMIN_TOKEN.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing administrator authorization token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return True


@router.post("/login", summary="Authenticate Administrator")
def admin_login(payload: AdminLoginRequest) -> Dict[str, Any]:
    """Validates administrator credentials and returns session bearer token."""
    if (
        payload.username.strip() == settings.ADMIN_USERNAME.strip()
        and payload.password.strip() == settings.ADMIN_PASSWORD.strip()
    ):
        return {
            "access_token": settings.ADMIN_TOKEN,
            "token_type": "bearer",
            "role": "admin",
            "username": settings.ADMIN_USERNAME,
            "message": "Authentication successful",
        }

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid administrator username or password.",
    )


@router.get("/stats", summary="Cohort Analytics and Growth Metrics")
def admin_stats(authenticated: bool = Depends(require_admin_auth)) -> Dict[str, Any]:
    """Returns aggregated analytics, employability tier distribution, and average improvement."""
    return get_admin_cohort_stats()


@router.get("/students", summary="Student Progression and Timestamps")
def admin_students(
    authenticated: bool = Depends(require_admin_auth),
) -> List[Dict[str, Any]]:
    """Returns enrolled students with timestamps, target roles, and evaluated improvement."""
    return get_admin_student_records()
