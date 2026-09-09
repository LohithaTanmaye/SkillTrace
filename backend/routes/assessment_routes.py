"""
assessment_routes.py: API endpoints for taking assessments, evaluating performance,
and converting assessment results into student skill profiles.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from backend.config import settings
from backend.schemas.assessment_schemas import (
    AssessmentEvaluateRawRequest,
    AssessmentEvaluateResponse,
    AssessmentSubmitRequest,
)
from backend.services.data_service import (
    load_assessment_questions,
    get_job_by_id,
)
from skilltrace_ai import (
    analyze_assessment,
    assessment_to_student_skills,
    analyze_student,
)

router = APIRouter(prefix="/assessment", tags=["Assessment"])


@router.get("/questions", response_model=List[Dict[str, Any]])
def get_questions(skill: Optional[str] = Query(None, description="Filter questions by skill name")):
    """
    Returns pre-assessment questions without exposing correct answer keys.
    """
    raw_questions = load_assessment_questions(skill=skill)
    # Strip correct_option before returning to client
    client_questions = []
    for q in raw_questions:
        client_questions.append({
            "question_id": q["question_id"],
            "skill": q["skill"],
            "question_text": q["question_text"],
            "options": q["options"],
            "difficulty": q["difficulty"],
        })
    return client_questions


@router.post("/evaluate", response_model=AssessmentEvaluateResponse)
def evaluate_raw_assessment(payload: AssessmentEvaluateRawRequest):
    """
    Evaluates raw assessment question & correct answer counts per skill.
    """
    try:
        raw_dict = {
            "assessment": [item.model_dump() for item in payload.assessment]
        }
        return analyze_assessment(raw_dict)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/submit")
def submit_assessment_answers(payload: AssessmentSubmitRequest):
    """
    Grades user-submitted answers, calculates skill proficiency levels (1-5),
    generates a student skill profile, and optionally executes immediate job alignment.
    """
    # Load all questions to verify answer keys
    all_questions = {q["question_id"]: q for q in load_assessment_questions()}

    # Aggregate performance by skill
    skill_stats: Dict[str, Dict[str, int]] = {}

    for answer in payload.answers:
        q_id = answer.question_id.strip()
        q_obj = all_questions.get(q_id)
        if not q_obj:
            continue

        skill = q_obj["skill"]
        if skill not in skill_stats:
            skill_stats[skill] = {"questions": 0, "correct": 0}

        skill_stats[skill]["questions"] += 1
        if answer.selected_option.strip().upper() == q_obj["correct_option"].strip().upper():
            skill_stats[skill]["correct"] += 1

    if not skill_stats:
        raise HTTPException(status_code=400, detail="No valid question answers were submitted.")

    # Format for analyze_assessment
    assessment_data = {
        "assessment": [
            {
                "skill": skill,
                "questions": stats["questions"],
                "correct_answers": stats["correct"],
            }
            for skill, stats in skill_stats.items()
        ]
    }

    eval_result = analyze_assessment(assessment_data)
    student_skills = assessment_to_student_skills(eval_result["evaluated_skills"])

    response_payload: Dict[str, Any] = {
        "evaluated_skills": eval_result["evaluated_skills"],
        "student_skills_profile": student_skills,
        "note": eval_result["note"],
        "job_analysis": None,
    }

    # Optional immediate job matching if target_job_id was provided
    if payload.target_job_id:
        target_job = get_job_by_id(payload.target_job_id)
        if target_job:
            analysis_input = {
                "job_title": target_job["title"],
                "student_skills": student_skills,
                "job_skills": target_job["job_skills"],
            }
            response_payload["job_analysis"] = analyze_student(
                analysis_input,
                enable_semantic=settings.ENABLE_SEMANTIC_MATCHING,
                semantic_threshold=settings.SEMANTIC_SIMILARITY_THRESHOLD,
            )

    return response_payload
