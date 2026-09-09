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
    load_jobs,
    get_job_by_id,
    add_student,
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

    # Optional automatic student registration if candidate details were provided
    registered_student = None
    if payload.student_name and payload.email:
        try:
            registered_student = add_student(
                name=payload.student_name,
                email=payload.email,
                student_skills=student_skills,
            )
        except Exception:
            pass

    response_payload: Dict[str, Any] = {
        "evaluated_skills": eval_result["evaluated_skills"],
        "student_skills_profile": student_skills,
        "registered_student": registered_student,
        "note": eval_result["note"],
        "job_analysis": None,
    }

    # Immediate job matching: supports target_job_id OR custom target_job_title
    target_job = None
    target_title = (payload.target_job_title or "").strip()
    target_skills = []

    # 1. Look up by ID if provided
    if payload.target_job_id:
        target_job = get_job_by_id(payload.target_job_id)
        if target_job:
            target_title = target_job["title"]
            target_skills = target_job["job_skills"]

    # 2. Look up by custom title if not resolved by ID
    if not target_job and target_title:
        clean_title = target_title.lower()
        all_jobs = load_jobs()
        for j in all_jobs:
            if clean_title == j["title"].lower() or clean_title in j["title"].lower() or j["title"].lower() in clean_title:
                target_job = j
                target_title = j["title"]
                target_skills = j["job_skills"]
                break

        # 3. Dynamic benchmark synthesis for completely custom dream roles
        if not target_skills:
            if any(k in clean_title for k in ["data", "analyst", "bi", "analytics"]):
                target_skills = [
                    {"name": "Python", "required_level": 4},
                    {"name": "SQL", "required_level": 4},
                    {"name": "Power BI", "required_level": 3},
                    {"name": "Excel", "required_level": 4},
                ]
            elif any(k in clean_title for k in ["front", "web", "react", "ui", "ux"]):
                target_skills = [
                    {"name": "JavaScript", "required_level": 4},
                    {"name": "HTML", "required_level": 4},
                    {"name": "CSS", "required_level": 4},
                    {"name": "React", "required_level": 3},
                    {"name": "Git", "required_level": 3},
                ]
            elif any(k in clean_title for k in ["cloud", "devops", "infra", "sre"]):
                target_skills = [
                    {"name": "Linux", "required_level": 4},
                    {"name": "Docker", "required_level": 4},
                    {"name": "AWS", "required_level": 3},
                    {"name": "Git", "required_level": 4},
                    {"name": "Python", "required_level": 3},
                ]
            elif any(k in clean_title for k in ["ml", "ai", "machine", "learning", "deep"]):
                target_skills = [
                    {"name": "Python", "required_level": 5},
                    {"name": "SQL", "required_level": 4},
                    {"name": "Machine Learning", "required_level": 4},
                    {"name": "Statistics", "required_level": 4},
                    {"name": "Docker", "required_level": 3},
                ]
            else:
                target_skills = [
                    {"name": "Python", "required_level": 4},
                    {"name": "FastAPI", "required_level": 3},
                    {"name": "SQL", "required_level": 4},
                    {"name": "Docker", "required_level": 3},
                    {"name": "Git", "required_level": 3},
                ]

    if target_skills:
        analysis_input = {
            "job_title": target_title or "Target Role",
            "student_skills": student_skills,
            "job_skills": target_skills,
        }
        analysis_result = analyze_student(
            analysis_input,
            enable_semantic=settings.ENABLE_SEMANTIC_MATCHING,
            semantic_threshold=settings.SEMANTIC_SIMILARITY_THRESHOLD,
        )
        analysis_result["job_title"] = target_title or "Target Role"
        response_payload["job_analysis"] = analysis_result

    return response_payload
