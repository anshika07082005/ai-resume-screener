from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from backend.auth import get_current_user
from backend.models import User

from backend.app.services.resume_parser import parse_resume
from backend.app.services.jd_parser import parse_job_description
from backend.app.services.matching_engine import match_candidate_to_job
from backend.app.services.interview_generator import (
    generate_interview_questions,
)

from backend.utils.extractor import extract_text_from_pdf


router = APIRouter(
    prefix="/api/v2/interview",
    tags=["V2 Interview Intelligence"],
)


@router.post("/generate")
async def generate_interview(
    resume: UploadFile = File(...),
    job_description: str = Form(""),
    jd_file: UploadFile | None = File(None),
    current_user: User = Depends(get_current_user),
):

    # ========================================================
    # RESUME VALIDATION
    # ========================================================

    if not resume.filename:
        raise HTTPException(
            status_code=400,
            detail="Resume file is required",
        )

    if not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF resumes are supported",
        )

    resume_text = extract_text_from_pdf(
        resume
    )

    if not resume_text.strip():
        raise HTTPException(
            status_code=422,
            detail="Could not extract readable resume text",
        )

    # ========================================================
    # JOB DESCRIPTION
    # ========================================================

    jd_text = job_description.strip()

    if jd_file is not None:

        if not jd_file.filename:
            raise HTTPException(
                status_code=400,
                detail="Invalid JD file",
            )

        if not jd_file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="Only PDF job descriptions are supported",
            )

        jd_text = extract_text_from_pdf(
            jd_file
        )

    if not jd_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Job description is required",
        )

    # ========================================================
    # PARSE + MATCH
    # ========================================================

    candidate = parse_resume(
        resume_text
    )

    job = parse_job_description(
        jd_text
    )

    match_data = match_candidate_to_job(
        candidate,
        job,
    )

    # ========================================================
    # GENERATE INTERVIEW QUESTIONS
    # ========================================================

    questions = generate_interview_questions(
        candidate,
        job,
        match_data,
    )

    return {
        "candidate_name": candidate.name,
        "job_title": job.title,
        "questions": questions,
    }