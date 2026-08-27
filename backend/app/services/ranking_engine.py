from typing import Dict


# ============================================================
# WEIGHTS
# ============================================================

WEIGHTS = {
    "skills": 0.35,
    "preferred_skills": 0.05,
    "semantic_similarity": 0.15,
    "projects": 0.15,
    "experience": 0.15,
    "education": 0.10,
    "certifications": 0.05,
}


# ============================================================
# SCORE NORMALIZATION
# ============================================================

def clamp_score(score: float) -> float:
    """
    Keep score between 0 and 100.
    """

    return max(
        0.0,
        min(float(score), 100.0),
    )


# ============================================================
# FINAL WEIGHTED SCORE
# ============================================================

def calculate_overall_score(
    match_data: Dict,
) -> float:
    """
    Combine matching signals using weighted scoring.
    """

    skill_score = clamp_score(
        match_data.get(
            "skill_score",
            0.0,
        )
    )

    preferred_score = clamp_score(
        match_data.get(
            "preferred_skill_score",
            0.0,
        )
    )

    semantic_score = clamp_score(
        match_data.get(
            "semantic_score",
            0.0,
        )
    )

    project_score = clamp_score(
        match_data.get(
            "project_score",
            0.0,
        )
    )

    experience_score = clamp_score(
        match_data.get(
            "experience_score",
            0.0,
        )
    )

    education_score = clamp_score(
        match_data.get(
            "education_score",
            0.0,
        )
    )

    certification_score = clamp_score(
        match_data.get(
            "certification_score",
            0.0,
        )
    )

    overall = (
        skill_score
        * WEIGHTS["skills"]
        +
        preferred_score
        * WEIGHTS["preferred_skills"]
        +
        semantic_score
        * WEIGHTS["semantic_similarity"]
        +
        project_score
        * WEIGHTS["projects"]
        +
        experience_score
        * WEIGHTS["experience"]
        +
        education_score
        * WEIGHTS["education"]
        +
        certification_score
        * WEIGHTS["certifications"]
    )

    return round(
        overall,
        2,
    )


# ============================================================
# RECOMMENDATION
# ============================================================

def get_recommendation(
    score: float,
) -> str:
    """
    Convert final numerical score into recruiter-friendly status.
    """

    if score >= 85:
        return "Strong Match"

    if score >= 70:
        return "Good Match"

    if score >= 55:
        return "Moderate Match"

    if score >= 40:
        return "Weak Match"

    return "Not Recommended"