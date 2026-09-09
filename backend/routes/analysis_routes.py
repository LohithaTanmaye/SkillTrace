"""
analysis_routes.py: API endpoints for running skill alignment, gap analysis, and recommendations.
"""

from fastapi import APIRouter, HTTPException
from backend.config import settings
from backend.schemas.skill_schemas import (
    AnalyzeStudentRequest,
    AnalysisResponse,
    MatchJobRequest,
)
from backend.services.data_service import prepare_analysis_payload
from skilltrace_ai import analyze_student

router = APIRouter(tags=["Analysis"])


@router.post("/analyze", response_model=AnalysisResponse)
def analyze(payload: AnalyzeStudentRequest):
    """
    Executes skill alignment analysis between submitted student skills
    and target job requirements.
    """
    try:
        raw_payload = {
            "job_title": payload.job_title or "Target Role",
            "student_skills": [s.model_dump() for s in payload.student_skills],
            "job_skills": [j.model_dump() for j in payload.job_skills],
        }

        result = analyze_student(
            raw_payload,
            enable_semantic=settings.ENABLE_SEMANTIC_MATCHING,
            semantic_threshold=settings.SEMANTIC_SIMILARITY_THRESHOLD,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/match-job", response_model=AnalysisResponse)
def match_stored_student_job(request: MatchJobRequest):
    """
    Loads a stored student profile and target benchmark job,
    then executes full gap analysis and scoring.
    """
    try:
        payload = prepare_analysis_payload(
            student_id=request.student_id,
            job_id=request.job_id,
        )
        result = analyze_student(
            payload,
            enable_semantic=settings.ENABLE_SEMANTIC_MATCHING,
            semantic_threshold=settings.SEMANTIC_SIMILARITY_THRESHOLD,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
