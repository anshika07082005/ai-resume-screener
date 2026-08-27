from typing import Dict, List


def generate_strengths(
    match_data: Dict,
) -> List[str]:

    strengths = []

    if match_data.get(
        "skill_score",
        0,
    ) >= 80:
        strengths.append(
            "Strong match with the job's required technical skills."
        )

    if match_data.get(
        "preferred_skill_score",
        0,
    ) >= 60:
        strengths.append(
            "Candidate matches several preferred skills."
        )

    if match_data.get(
        "semantic_score",
        0,
    ) >= 70:
        strengths.append(
            "Overall resume content is highly relevant to the job description."
        )

    if match_data.get(
        "project_score",
        0,
    ) >= 70:
        strengths.append(
            "Candidate projects strongly align with the role."
        )

    if match_data.get(
        "experience_score",
        0,
    ) >= 70:
        strengths.append(
            "Candidate experience is relevant to the position."
        )

    if match_data.get(
        "education_score",
        0,
    ) >= 70:
        strengths.append(
            "Educational background aligns well with job requirements."
        )

    if match_data.get(
        "certification_score",
        0,
    ) >= 60:
        strengths.append(
            "Relevant certifications strengthen the candidate profile."
        )

    matched_skills = match_data.get(
        "matched_skills",
        [],
    )

    if matched_skills:
        preview = ", ".join(
            matched_skills[:6]
        )

        strengths.append(
            f"Matched required skills: {preview}."
        )

    return strengths


def generate_weaknesses(
    match_data: Dict,
) -> List[str]:

    weaknesses = []

    missing_skills = match_data.get(
        "missing_skills",
        [],
    )

    if missing_skills:
        preview = ", ".join(
            missing_skills[:6]
        )

        weaknesses.append(
            f"Missing required skills: {preview}."
        )

    if match_data.get(
        "skill_score",
        0,
    ) < 60:
        weaknesses.append(
            "Required technical skill coverage is below the preferred threshold."
        )

    if match_data.get(
        "project_score",
        0,
    ) < 50:
        weaknesses.append(
            "Projects show limited direct relevance to this role."
        )

    if match_data.get(
        "experience_score",
        0,
    ) < 50:
        weaknesses.append(
            "Professional experience has limited relevance to the job description."
        )

    if match_data.get(
        "education_score",
        0,
    ) < 50:
        weaknesses.append(
            "Educational background does not strongly match the stated qualification requirements."
        )

    if match_data.get(
        "semantic_score",
        0,
    ) < 50:
        weaknesses.append(
            "Overall resume content has low semantic similarity with the job description."
        )

    return weaknesses