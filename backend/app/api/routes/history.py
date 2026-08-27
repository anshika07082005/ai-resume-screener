import json

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from backend.auth import (
    get_current_user,
)

from backend.database import (
    get_db,
)

from backend.models import (
    ScreeningResult,
    User,
)


router = APIRouter(
    prefix="/api/v2/history",
    tags=["V2 Screening History"],
)


def parse_json_field(
    value,
):
    if not value:
        return []

    try:
        return json.loads(
            value
        )

    except Exception:
        return []


@router.get("")
def get_screening_history(
    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_db
    ),
):
    records = (
        db.query(ScreeningResult)
        .filter(
            ScreeningResult.user_id
            == current_user.id
        )
        .order_by(
            ScreeningResult.created_at.desc()
        )
        .all()
    )

    return [
        {
            "id": record.id,

            "candidate_name":
                record.candidate_name,

            "job_title":
                record.job_title,

            "overall_score":
                record.overall_score,

            "recommendation":
                record.recommendation,

            "breakdown": {
                "skills":
                    record.skill_score,

                "preferred_skills":
                    record.preferred_skill_score,

                "semantic_similarity":
                    record.semantic_score,

                "projects":
                    record.project_score,

                "experience":
                    record.experience_score,

                "education":
                    record.education_score,

                "certifications":
                    record.certification_score,
            },

            "matched_skills":
                parse_json_field(
                    record.matched_skills
                ),

            "missing_skills":
                parse_json_field(
                    record.missing_skills
                ),

            "matched_preferred_skills":
                parse_json_field(
                    record.matched_preferred_skills
                ),

            "strengths":
                parse_json_field(
                    record.strengths
                ),

            "weaknesses":
                parse_json_field(
                    record.weaknesses
                ),

            "created_at": (
                record.created_at.isoformat()
                if record.created_at
                else None
            ),
        }

        for record in records
    ]


@router.get(
    "/{screening_id}"
)
def get_screening(
    screening_id: int,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_db
    ),
):
    record = (
        db.query(ScreeningResult)
        .filter(
            ScreeningResult.id
            == screening_id,

            ScreeningResult.user_id
            == current_user.id,
        )
        .first()
    )

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Screening result not found",
        )

    return {
        "id": record.id,

        "candidate_name":
            record.candidate_name,

        "job_title":
            record.job_title,

        "overall_score":
            record.overall_score,

        "recommendation":
            record.recommendation,

        "breakdown": {
            "skills":
                record.skill_score,

            "preferred_skills":
                record.preferred_skill_score,

            "semantic_similarity":
                record.semantic_score,

            "projects":
                record.project_score,

            "experience":
                record.experience_score,

            "education":
                record.education_score,

            "certifications":
                record.certification_score,
        },

        "matched_skills":
            parse_json_field(
                record.matched_skills
            ),

        "missing_skills":
            parse_json_field(
                record.missing_skills
            ),

        "matched_preferred_skills":
            parse_json_field(
                record.matched_preferred_skills
            ),

        "strengths":
            parse_json_field(
                record.strengths
            ),

        "weaknesses":
            parse_json_field(
                record.weaknesses
            ),

        "created_at": (
            record.created_at.isoformat()
            if record.created_at
            else None
        ),
    }