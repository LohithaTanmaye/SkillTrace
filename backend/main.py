"""
main.py: FastAPI entrypoint for SKILLTRACE backend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.routes.analysis_routes import router as analysis_router
from backend.routes.assessment_routes import router as assessment_router
from backend.routes.job_routes import router as job_router
from backend.routes.student_routes import router as student_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Explainable student skill analysis and job-readiness platform for SIH 2026",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for local development and frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(analysis_router)
app.include_router(assessment_router)
app.include_router(job_router)
app.include_router(student_router)


@app.get("/", tags=["System"])
def root():
    """System welcome and operational metadata."""
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "status": "online",
        "documentation": "/docs",
        "endpoints": {
            "jobs": "/jobs",
            "students": "/students",
            "assessment_questions": "/assessment/questions",
            "analyze": "POST /analyze",
            "match_job": "POST /match-job",
            "submit_assessment": "POST /assessment/submit",
        },
    }


@app.get("/health", tags=["System"])
def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "semantic_matching_enabled": settings.ENABLE_SEMANTIC_MATCHING,
        "semantic_threshold": settings.SEMANTIC_SIMILARITY_THRESHOLD,
    }
