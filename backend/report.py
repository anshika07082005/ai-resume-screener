from fastapi import APIRouter
from fastapi.responses import FileResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import tempfile

router = APIRouter()

@router.get("/download-report")
def download_report(match_score: float, matched_skills: str, missing_skills: str):
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(temp.name, pagesize=A4)

    y = 800
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "AI Resume Screening Report")

    y -= 40
    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Match Score: {round(match_score * 100, 2)}%")

    y -= 30
    c.drawString(50, y, "Matched Skills:")
    y -= 20
    for s in matched_skills.split(","):
        c.drawString(70, y, f"- {s}")
        y -= 15

    y -= 10
    c.drawString(50, y, "Missing Skills:")
    y -= 20
    for s in missing_skills.split(","):
        c.drawString(70, y, f"- {s}")
        y -= 15

    c.save()
    return FileResponse(temp.name, filename="resume_report.pdf")
