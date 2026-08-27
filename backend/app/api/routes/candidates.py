from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.app.schemas.candidate import CandidateProfile
from backend.app.services.resume_parser import parse_resume
from backend.utils.extractor import extract_text_from_pdf


router = APIRouter(
    prefix="/api/v2/candidates",
    tags=["V2 Candidates"],
)


@router.post(
    "/parse-resume",
    response_model=CandidateProfile,
)
async def parse_candidate_resume(
    resume: UploadFile = File(...),
):
    if not resume.filename:
        raise HTTPException(
            status_code=400,
            detail="Resume file is required",
        )

    if not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF resumes are supported currently",
        )

    text = extract_text_from_pdf(resume)

    if not text.strip():
        raise HTTPException(
            status_code=422,
            detail="Could not extract readable text from resume",
        )

    return parse_resume(text)