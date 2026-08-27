import json

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from sqlalchemy.orm import Session

from backend.app.schemas.screening import (
    ScoreBreakdown,
    ScreeningResult as ScreeningResponse,
)

from backend.app.services.resume_parser import (
    parse_resume,
)

from backend.app.services.jd_parser import (
    parse_job_description,
)

from backend.app.services.matching_engine import (
    match_candidate_to_job,
)

from backend.app.services.ranking_engine import (
    calculate_overall_score,
    get_recommendation,
)

from backend.app.services.explanation_engine import (
    generate_strengths,
    generate_weaknesses,
)

from backend.auth import (
    get_current_user,
)

from backend.database import (
    get_db,
)

from backend.models import (
    Candidate,
    Job,
    ScreeningResult as ScreeningModel,
    User,
)

from backend.utils.extractor import (
    extract_text_from_pdf,
)


router = APIRouter(
    prefix="/api/v2",
    tags=["V2 Screening"],
)


@router.post(
    "/screen",
    response_model=ScreeningResponse,
)
async def screen_candidate(
    resume: UploadFile = File(...),
    job_description: str = Form(""),
    jd_file: UploadFile | None = File(None),

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_db
    ),
):
    """
    Complete authenticated V2 candidate screening pipeline.

    The result is also persisted in the database.
    """

    # ========================================================
    # VALIDATE RESUME
    # ========================================================

    if not resume.filename:
        raise HTTPException(
            status_code=400,
            detail="Resume file is required",
        )

    if not resume.filename.lower().endswith(
        ".pdf"
    ):
        raise HTTPException(
            status_code=400,
            detail="Only PDF resumes are currently supported",
        )

    # ========================================================
    # EXTRACT RESUME TEXT
    # ========================================================

    resume_text = extract_text_from_pdf(
        resume
    )

    if not resume_text.strip():
        raise HTTPException(
            status_code=422,
            detail="Could not extract readable text from resume",
        )

    # ========================================================
    # EXTRACT JOB DESCRIPTION
    # ========================================================

    jd_text = job_description.strip()

    if jd_file is not None:

        if not jd_file.filename:
            raise HTTPException(
                status_code=400,
                detail="Invalid JD file",
            )

        if not jd_file.filename.lower().endswith(
            ".pdf"
        ):
            raise HTTPException(
                status_code=400,
                detail="Only PDF job descriptions are currently supported",
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
    # PARSE CANDIDATE
    # ========================================================

    candidate = parse_resume(
        resume_text
    )

    # ========================================================
    # PARSE JOB
    # ========================================================

    job = parse_job_description(
        jd_text
    )

    # ========================================================
    # HYBRID MATCHING
    # ========================================================

    match_data = match_candidate_to_job(
        candidate,
        job,
    )

    # ========================================================
    # FINAL SCORE
    # ========================================================

    overall_score = calculate_overall_score(
        match_data
    )

    recommendation = get_recommendation(
        overall_score
    )

    # ========================================================
    # EXPLAINABILITY
    # ========================================================

    strengths = generate_strengths(
        match_data
    )

    weaknesses = generate_weaknesses(
        match_data
    )

    # ========================================================
    # SAVE CANDIDATE
    # ========================================================

    candidate_record = Candidate(
        user_id=current_user.id,

        name=candidate.name,

        email=candidate.email,

        phone=candidate.phone,

        skills=json.dumps(
            candidate.skills
        ),

        education=json.dumps(
            [
                item.model_dump()
                for item in candidate.education
            ]
        ),

        experience=json.dumps(
            [
                item.model_dump()
                for item in candidate.experience
            ]
        ),

        projects=json.dumps(
            [
                item.model_dump()
                for item in candidate.projects
            ]
        ),

        certifications=json.dumps(
            candidate.certifications
        ),

        raw_text=candidate.raw_text,
    )

    db.add(
        candidate_record
    )

    db.flush()

    # ========================================================
    # SAVE JOB
    # ========================================================

    job_record = Job(
        user_id=current_user.id,

        title=job.title,

        description=job.raw_text or jd_text,

        required_skills=json.dumps(
            job.required_skills
        ),

        preferred_skills=json.dumps(
            job.preferred_skills
        ),

        minimum_experience=(
            job.minimum_experience
        ),

        education_requirements=json.dumps(
            job.education_requirements
        ),

        responsibilities=json.dumps(
            job.responsibilities
        ),
    )

    db.add(
        job_record
    )

    db.flush()

    # ========================================================
    # SAVE SCREENING RESULT
    # ========================================================

    screening_record = ScreeningModel(
        user_id=current_user.id,

        candidate_id=candidate_record.id,

        job_id=job_record.id,

        candidate_name=candidate.name,

        job_title=job.title,

        overall_score=overall_score,

        skill_score=match_data.get(
            "skill_score",
            0.0,
        ),

        preferred_skill_score=match_data.get(
            "preferred_skill_score",
            0.0,
        ),

        semantic_score=match_data.get(
            "semantic_score",
            0.0,
        ),

        project_score=match_data.get(
            "project_score",
            0.0,
        ),

        experience_score=match_data.get(
            "experience_score",
            0.0,
        ),

        education_score=match_data.get(
            "education_score",
            0.0,
        ),

        certification_score=match_data.get(
            "certification_score",
            0.0,
        ),

        matched_skills=json.dumps(
            match_data.get(
                "matched_skills",
                [],
            )
        ),

        missing_skills=json.dumps(
            match_data.get(
                "missing_skills",
                [],
            )
        ),

        matched_preferred_skills=json.dumps(
            match_data.get(
                "matched_preferred_skills",
                [],
            )
        ),

        strengths=json.dumps(
            strengths
        ),

        weaknesses=json.dumps(
            weaknesses
        ),

        recommendation=recommendation,
    )

    db.add(
        screening_record
    )

    db.commit()

    # ========================================================
    # RESPONSE
    # ========================================================

    return ScreeningResponse(
        candidate_name=candidate.name,

        job_title=job.title,

        overall_score=overall_score,

        breakdown=ScoreBreakdown(
            skills=match_data.get(
                "skill_score",
                0.0,
            ),

            preferred_skills=match_data.get(
                "preferred_skill_score",
                0.0,
            ),

            semantic_similarity=match_data.get(
                "semantic_score",
                0.0,
            ),

            projects=match_data.get(
                "project_score",
                0.0,
            ),

            experience=match_data.get(
                "experience_score",
                0.0,
            ),

            education=match_data.get(
                "education_score",
                0.0,
            ),

            certifications=match_data.get(
                "certification_score",
                0.0,
            ),
        ),

        matched_skills=match_data.get(
            "matched_skills",
            [],
        ),

        missing_skills=match_data.get(
            "missing_skills",
            [],
        ),

        matched_preferred_skills=match_data.get(
            "matched_preferred_skills",
            [],
        ),

        strengths=strengths,

        weaknesses=weaknesses,

        recommendation=recommendation,
    )