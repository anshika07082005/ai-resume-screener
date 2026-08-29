from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.auth import (
    router as auth_router,
)

from backend.screen import (
    router as screen_router,
)

from backend.report import (
    router as report_router,
)

from backend.database import (
    engine,
)

from backend.models import (
    Base,
)

from backend.app.api.routes.candidates import (
    router as candidate_router,
)

from backend.app.api.routes.jobs import (
    router as jobs_router,
)

from backend.app.api.routes.screening import (
    router as screening_router,
)

from backend.app.api.routes.history import (
    router as history_router,
)

from backend.app.api.routes.interview import (
    router as interview_router,
)


app = FastAPI(
    title="AI Resume Screener API",
    description=(
        "AI-powered resume screening and hiring intelligence platform "
        "with structured resume parsing, job-description intelligence, "
        "semantic candidate-job matching, explainable scoring, "
        "screening history, and personalized interview intelligence."
    ),
    version="2.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# DATABASE
# ============================================================

Base.metadata.create_all(
    bind=engine
)


# ============================================================
# AUTHENTICATION
# ============================================================

app.include_router(
    auth_router
)


# ============================================================
# LEGACY V1
# ============================================================

app.include_router(
    screen_router
)

app.include_router(
    report_router
)


# ============================================================
# V2
# ============================================================

app.include_router(
    candidate_router
)

app.include_router(
    jobs_router
)

app.include_router(
    screening_router
)

app.include_router(
    history_router
)

app.include_router(
    interview_router
)


# ============================================================
# SYSTEM ENDPOINTS
# ============================================================

@app.get("/")
def root():
    return {
        "message": (
            "AI Resume Screener "
            "backend running successfully"
        ),
        "version": "2.0.0",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "AI Resume Screener",
        "version": "2.0.0",
    }