"""
skill_schemas.py: Pydantic models for skill profile analysis and job matching.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SkillItem(BaseModel):
    name: str = Field(..., description="Name of the skill, e.g. 'Python'")
    level: int = Field(..., ge=0, le=5, description="Proficiency level (0-5)")


class RequiredSkillItem(BaseModel):
    name: str = Field(..., description="Name of required skill")
    required_level: int = Field(..., ge=1, le=5, description="Required proficiency level (1-5)")


class AnalyzeStudentRequest(BaseModel):
    job_title: Optional[str] = Field("Target Role", description="Target job title")
    student_skills: List[SkillItem] = Field(..., description="List of student skills")
    job_skills: List[RequiredSkillItem] = Field(..., description="List of required job skills")


class MatchJobRequest(BaseModel):
    student_id: str = Field(..., description="Identifier of the stored student, e.g. 'STU001'")
    job_id: str = Field(..., description="Identifier of the benchmark job, e.g. 'JOB001'")


class EvaluatedSkillDetail(BaseModel):
    name: str
    required_level: int
    student_level: int
    deficit: int
    match_ratio: float
    match_type: str
    confidence: float
    category: str


class RecommendationItem(BaseModel):
    priority_rank: int
    skill: str
    urgency: str
    current_level: int
    target_level: int
    title: str
    action: str
    estimated_effort_weeks: int


class PrioritizedGapItem(BaseModel):
    name: str
    category: str
    student_level: int
    required_level: int
    deficit: int
    priority_score: int
    urgency: str
    rationale: str
    rank: int


class AnalysisResponse(BaseModel):
    match_score: float
    matched_skills: List[Dict[str, Any]]
    partial_gaps: List[Dict[str, Any]]
    missing_skills: List[Dict[str, Any]]
    skill_gaps: List[Dict[str, Any]]
    prioritized_gaps: List[PrioritizedGapItem]
    recommendations: List[RecommendationItem]
    explanation: str
    explanation_details: Dict[str, Any]
    score_breakdown: List[Dict[str, Any]]
    disclaimer: str
