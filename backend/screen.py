from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from utils.extractor import extract_text_from_pdf
from utils.skills import extract_skills
from utils.similarity import skill_similarity
from utils.fit_score import (
    calculate_fit_score,
    predict_role_category,
    ats_score,
    resume_suggestions,
    learning_roadmap
)

router = APIRouter()

@router.post("/screen-pdf")
async def screen_resume(
    resume: UploadFile = File(...),
    jd_file: UploadFile | None = File(None),
    job_description: str = Form("")
):
    resume_text = extract_text_from_pdf(resume)
    jd_text = extract_text_from_pdf(jd_file) if jd_file else job_description.strip()

    if not jd_text:
        raise HTTPException(status_code=400, detail="Job description required")

    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)

    matched, missing = skill_similarity(resume_skills, jd_skills)
    score = calculate_fit_score(matched, jd_skills)

    return {
        "match_score": score,
        "matched_skills": matched,
        "missing_skills": missing,

        # Extra features 
        "predicted_role": predict_role_category(jd_text),
        "ats_score": ats_score(resume_text),
        "resume_suggestions": resume_suggestions(missing),
        "learning_roadmap": learning_roadmap(missing)
    }
