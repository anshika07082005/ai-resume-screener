from utils.skills import get_skill_weight

# ROLE PREDICTION
def predict_role_category(text: str) -> str:
    text = text.lower()

    if any(k in text for k in [
        "machine learning", "deep learning", "nlp",
        "computer vision", "artificial intelligence"
    ]):
        return "AI / ML Engineer"

    if any(k in text for k in [
        "data analyst", "data scientist", "pandas",
        "numpy", "sql", "tableau", "power bi"
    ]):
        return "Data Scientist / Analyst"

    if any(k in text for k in [
        "backend", "api", "fastapi", "flask",
        "django", "spring", "microservices"
    ]):
        return "Backend Developer"

    if any(k in text for k in [
        "react", "angular", "vue", "frontend",
        "javascript", "css", "html"
    ]):
        return "Frontend Developer"

    if any(k in text for k in [
        "aws", "docker", "kubernetes",
        "ci/cd", "devops", "terraform"
    ]):
        return "DevOps / Cloud Engineer"

    return "Software Engineer"

# ATS COMPATIBILITY SCORE
def ats_score(resume_text: str) -> float:
    """
    Estimates how ATS-friendly a resume is.
    Penalizes elements ATS systems struggle with.
    """

    text = resume_text.lower()
    penalty = 0.0

    # Heuristic penalties
    if "table" in text:
        penalty += 0.15
    if "image" in text:
        penalty += 0.15
    if "graphic" in text:
        penalty += 0.10
    if "column" in text:
        penalty += 0.10

    score = 1.0 - penalty
    return round(max(0.0, min(score, 1.0)), 2)


# WEIGHTED FIT SCORE (CORE LOGIC)
def calculate_fit_score(matched_skills: list, jd_skills: list) -> float:
    """
    Computes a weighted fit score based on
    skill category importance.
    """

    if not jd_skills:
        return 0.0

    matched_set = set(matched_skills)

    total_weight = 0.0
    matched_weight = 0.0

    for skill in jd_skills:
        weight = get_skill_weight(skill)
        total_weight += weight

        if skill in matched_set:
            matched_weight += weight

    if total_weight == 0:
        return 0.0

    return round(matched_weight / total_weight, 3)


# RESUME IMPROVEMENT SUGGESTIONS
def resume_suggestions(missing_skills: list) -> list:
    """
    Generates human-readable suggestions
    to improve resume quality.
    """

    suggestions = []

    for skill in missing_skills:
        suggestions.append(
            f"Add hands-on experience or a project demonstrating '{skill}' to strengthen your profile."
        )

    return suggestions


# LEARNING ROADMAP GENERATOR
def learning_roadmap(missing_skills: list) -> dict:
    """
    Generates a structured learning roadmap
    for missing skills.
    """

    roadmap = {}

    for skill in missing_skills:
        roadmap[skill] = [
            "Learn core concepts and fundamentals",
            "Build a small practical project",
            "Apply the skill in a real-world or open-source project"
        ]

    return roadmap
