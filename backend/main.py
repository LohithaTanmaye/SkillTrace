"""
main.py: FastAPI entrypoint for SKILLTRACE backend and frontend static hosting.
"""

from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.config import settings
from backend.routes.analysis_routes import router as analysis_router
from backend.routes.assessment_routes import router as assessment_router
from backend.routes.job_routes import router as job_router
from backend.routes.student_routes import router as student_router
from backend.routes.admin_routes import router as admin_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Explainable student skill analysis and job-readiness platform for SIH 2026",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register REST API routers
app.include_router(analysis_router)
app.include_router(assessment_router)
app.include_router(job_router)
app.include_router(student_router)
app.include_router(admin_router)


@app.get("/api/meta", tags=["System"])
def system_metadata():
    """System status and endpoint metadata."""
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "status": "online",
        "documentation": "/docs",
    }


@app.get("/health", tags=["System"])
def health_check():
    """Health check endpoint for platform monitoring."""
    return {
        "status": "healthy",
        "semantic_matching_enabled": settings.ENABLE_SEMANTIC_MATCHING,
        "semantic_threshold": settings.SEMANTIC_SIMILARITY_THRESHOLD,
    }


# Mount Frontend static assets and HTML pages
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
