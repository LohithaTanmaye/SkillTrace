"""
assessment_schemas.py: Pydantic models for pre-assessment questions and submissions.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AssessmentQuestionResponse(BaseModel):
    question_id: str
    skill: str
    question_text: str
    options: Dict[str, str]
    difficulty: str


class AssessmentAnswerSubmission(BaseModel):
    question_id: str = Field(..., description="ID of the question answered")
    selected_option: str = Field(..., description="Selected option ('A', 'B', 'C', or 'D')")


class AssessmentSubmitRequest(BaseModel):
    student_id: Optional[str] = Field(None, description="Optional student ID to associate results with")
    student_name: Optional[str] = Field(None, description="Optional student full name for new user registration")
    email: Optional[str] = Field(None, description="Optional student email address")
    degree: Optional[str] = Field(None, description="Optional academic major or degree")
    answers: List[AssessmentAnswerSubmission] = Field(..., description="List of user's submitted answers")
    target_job_id: Optional[str] = Field(None, description="Optional target job ID to immediately run matching")


class AssessmentItemRaw(BaseModel):
    skill: str = Field(..., description="Skill name")
    questions: int = Field(..., gt=0, description="Total questions attempted")
    correct_answers: int = Field(..., ge=0, description="Number of correct answers")


class AssessmentEvaluateRawRequest(BaseModel):
    assessment: List[AssessmentItemRaw]


class EvaluatedSkillItem(BaseModel):
    skill: str
    questions: int
    correct_answers: int
    percentage: float
    estimated_level: int
    proficiency_label: str


class AssessmentEvaluateResponse(BaseModel):
    evaluated_skills: List[EvaluatedSkillItem]
    note: str
