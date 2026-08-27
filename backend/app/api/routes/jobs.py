from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from backend.app.schemas.job import (
    JobProfile,
)
from backend.app.services.jd_parser import (
    parse_job_description,
)
from backend.utils.extractor import (
    extract_text_from_pdf,
)


router = APIRouter(
    prefix="/api/v2/jobs",
    tags=["V2 Jobs"],
)


@router.post(
    "/parse",
    response_model=JobProfile,
)
async def parse_job(
    job_description: str = Form(""),
    jd_file: UploadFile | None = File(None),
):
    """
    Parse either pasted JD text or an uploaded JD PDF.
    """

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

    job_profile = parse_job_description(
        jd_text
    )

    return job_profile