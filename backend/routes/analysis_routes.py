"""
analysis_routes.py: API endpoints for running skill alignment, gap analysis,
recommendations, and multi-role career matching.
"""

from typing import List
from fastapi import APIRouter, HTTPException
from backend.config import settings
from backend.schemas.skill_schemas import (
    AnalyzeStudentRequest,
    AnalysisResponse,
    MatchJobRequest,
    MultiRoleAnalysisResponse,
    RoleRecommendationItem,
    SkillItem,
)
from backend.services.data_service import prepare_analysis_payload, load_jobs
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


@router.post("/analyze/all-roles", response_model=MultiRoleAnalysisResponse)
def match_all_career_roles(student_skills: List[SkillItem]):
    """
    Evaluates a student's skills against ALL available benchmark jobs in the system,
    ranking them by match score to determine which roles the student is eligible
    to apply for right now vs what to target after upskilling.
    """
    try:
        all_jobs = load_jobs()
        skills_raw = [s.model_dump() for s in student_skills]
        ranked_roles: List[RoleRecommendationItem] = []

        for job in all_jobs:
            payload = {
                "job_title": job["title"],
                "student_skills": skills_raw,
                "job_skills": job["job_skills"],
            }
            res = analyze_student(
                payload,
                enable_semantic=settings.ENABLE_SEMANTIC_MATCHING,
                semantic_threshold=settings.SEMANTIC_SIMILARITY_THRESHOLD,
            )

            score = res["match_score"]
            if score >= 70.0:
                tier = "Ready to Apply"
            elif score >= 45.0:
                tier = "Close Match"
            else:
                tier = "Future Target"

            matched_names = [m["name"] for m in res["matched_skills"]]
            missing_names = [g["name"] for g in res["skill_gaps"]][:3]

            ranked_roles.append(
                RoleRecommendationItem(
                    job_id=job["job_id"],
                    title=job["title"],
                    domain=job["domain"],
                    experience_level=job["experience_level"],
                    match_score=score,
                    fit_tier=tier,
                    matched_skills_count=len(res["matched_skills"]),
                    gaps_count=len(res["skill_gaps"]),
                    matched_skill_names=matched_names,
                    top_missing_skills=missing_names,
                )
            )

        # Sort descending by match_score
        ranked_roles.sort(key=lambda r: r.match_score, reverse=True)

        best_fit = ranked_roles[0] if ranked_roles else None

        return MultiRoleAnalysisResponse(
            ranked_roles=ranked_roles,
            best_fit_role=best_fit,
            total_roles_evaluated=len(ranked_roles),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
