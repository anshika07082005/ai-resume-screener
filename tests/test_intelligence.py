from backend.app.services.jd_parser import (
    parse_job_description,
)

from backend.app.services.ranking_engine import (
    calculate_overall_score,
    get_recommendation,
)


TEST_JOB_DESCRIPTION = """
Job Title: Junior Machine Learning Engineer

Responsibilities:
- Build and evaluate machine learning models.
- Develop Python applications.
- Build REST APIs using FastAPI.
- Work with structured datasets.

Required Skills:
- Python
- Machine Learning
- Scikit-Learn
- Pandas
- NumPy
- SQL
- FastAPI
- Git

Preferred Skills:
- AWS
- Docker
- MongoDB
- NLP

Qualifications:
Bachelor's degree in Computer Science,
Artificial Intelligence,
Machine Learning,
Data Science,
Information Technology,
or a related technical field.

Experience:
0-2 years of relevant experience.
Fresh graduates are encouraged to apply.
"""


# ============================================================
# JD PARSER
# ============================================================

def test_job_title_parsing():

    job = parse_job_description(
        TEST_JOB_DESCRIPTION
    )

    assert (
        job.title
        == "Junior Machine Learning Engineer"
    )


def test_required_skill_parsing():

    job = parse_job_description(
        TEST_JOB_DESCRIPTION
    )

    expected = {
        "python",
        "machine learning",
        "scikit-learn",
        "pandas",
        "numpy",
        "sql",
        "fastapi",
        "git",
    }

    assert (
        set(job.required_skills)
        == expected
    )


def test_preferred_skill_parsing():

    job = parse_job_description(
        TEST_JOB_DESCRIPTION
    )

    expected = {
        "aws",
        "docker",
        "mongodb",
        "nlp",
    }

    assert (
        set(job.preferred_skills)
        == expected
    )


def test_required_and_preferred_skills_are_separate():

    job = parse_job_description(
        TEST_JOB_DESCRIPTION
    )

    required = set(
        job.required_skills
    )

    preferred = set(
        job.preferred_skills
    )

    assert required.isdisjoint(
        preferred
    )


def test_entry_level_experience_parsing():

    job = parse_job_description(
        TEST_JOB_DESCRIPTION
    )

    assert (
        job.minimum_experience
        == 0
    )


# ============================================================
# RANKING ENGINE
# ============================================================

def test_overall_score_calculation():

    match_data = {
        "skill_score": 100,
        "preferred_skill_score": 75,
        "semantic_score": 60,
        "project_score": 50,
        "experience_score": 70,
        "education_score": 80,
        "certification_score": 50,
    }

    score = calculate_overall_score(
        match_data
    )

    assert 0 <= score <= 100

    assert isinstance(
        score,
        float
    )


def test_good_match_recommendation():

    assert (
        get_recommendation(75)
        == "Good Match"
    )


def test_strong_match_recommendation():

    assert (
        get_recommendation(90)
        == "Strong Match"
    )


def test_moderate_match_recommendation():

    assert (
        get_recommendation(60)
        == "Moderate Match"
    )


def test_not_recommended():

    assert (
        get_recommendation(20)
        == "Not Recommended"
    )