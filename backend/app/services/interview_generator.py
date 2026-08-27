from typing import Dict, List

from backend.app.schemas.candidate import CandidateProfile
from backend.app.schemas.job import JobProfile


def generate_interview_questions(
    candidate: CandidateProfile,
    job: JobProfile,
    match_data: Dict,
) -> Dict[str, List[str]]:

    technical_questions = []
    project_questions = []
    skill_gap_questions = []
    experience_questions = []

    matched_skills = match_data.get(
        "matched_skills",
        [],
    )

    missing_skills = match_data.get(
        "missing_skills",
        [],
    )

    matched_preferred_skills = match_data.get(
        "matched_preferred_skills",
        [],
    )

    # ========================================================
    # TECHNICAL QUESTIONS
    # ========================================================

    for skill in matched_skills[:5]:
        technical_questions.append(
            f"Explain a practical situation or project where you used {skill}."
        )

    if "machine learning" in matched_skills:
        technical_questions.append(
            "How do you evaluate a machine learning model, "
            "and how do you decide which evaluation metric to prioritize?"
        )

    if "python" in matched_skills:
        technical_questions.append(
            "How would you structure a Python machine learning "
            "application for maintainability and scalability?"
        )

    if "fastapi" in matched_skills:
        technical_questions.append(
            "How would you expose a trained machine learning "
            "model through a FastAPI REST API?"
        )

    if "sql" in matched_skills:
        technical_questions.append(
            "How would you troubleshoot and optimize a slow SQL "
            "query used inside a data-processing pipeline?"
        )

    # ========================================================
    # PROJECT QUESTIONS
    # ========================================================

    for project in candidate.projects[:3]:

        project_questions.append(
            f"In your project '{project.name}', what was the "
            "biggest technical challenge and how did you solve it?"
        )

        project_questions.append(
            f"What important technical or model-selection decisions "
            f"did you make in '{project.name}', and why?"
        )

    # ========================================================
    # SKILL GAP QUESTIONS
    # ========================================================

    for skill in missing_skills[:5]:

        skill_gap_questions.append(
            f"This role requires {skill}. How would you approach "
            "learning and applying it in a real project?"
        )

    for skill in matched_preferred_skills[:3]:

        skill_gap_questions.append(
            f"You have exposure to {skill}. How would you apply "
            "it effectively in this role?"
        )

    # ========================================================
    # EXPERIENCE QUESTIONS
    # ========================================================

    for experience in candidate.experience[:2]:

        experience_questions.append(
            f"Tell me about your experience at {experience.company} "
            f"as {experience.role}. What did you personally contribute?"
        )

        experience_questions.append(
            f"What was one problem you faced during your time at "
            f"{experience.company}, and how did you resolve it?"
        )

    # ========================================================
    # BEHAVIORAL QUESTIONS
    # ========================================================

    behavioral_questions = [
        "Tell me about a time you had to learn a new technology quickly.",
        "Describe a situation where your first technical approach did not work. What did you change?",
        "How do you prioritize tasks when working on multiple technical requirements?",
        "Tell me about a time you received critical feedback and how you responded.",
        "Why are you interested in this role and how does it align with your career goals?",
    ]

    return {
        "technical_questions": technical_questions[:8],
        "project_questions": project_questions[:6],
        "skill_gap_questions": skill_gap_questions[:5],
        "experience_questions": experience_questions[:4],
        "behavioral_questions": behavioral_questions,
    }