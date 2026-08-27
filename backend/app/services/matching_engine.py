from typing import Dict, List, Tuple

from backend.app.ml.embeddings import semantic_similarity
from backend.app.schemas.candidate import CandidateProfile
from backend.app.schemas.job import JobProfile


# ============================================================
# HELPERS
# ============================================================

def normalize_skills(
    skills: List[str],
) -> set[str]:
    """
    Normalize skills for exact matching.
    """

    return {
        skill.strip().lower()
        for skill in skills
        if skill and skill.strip()
    }


def clamp_score(
    score: float,
) -> float:
    """
    Keep scores between 0 and 100.
    """

    return round(
        max(
            0.0,
            min(float(score), 100.0),
        ),
        2,
    )


# ============================================================
# REQUIRED SKILLS
# ============================================================

def calculate_skill_match(
    candidate: CandidateProfile,
    job: JobProfile,
) -> Tuple[float, List[str], List[str]]:
    """
    Required skills are treated as hard technical evidence.
    """

    candidate_skills = normalize_skills(
        candidate.skills
    )

    required_skills = normalize_skills(
        job.required_skills
    )

    if not required_skills:
        return 0.0, [], []

    matched = sorted(
        candidate_skills.intersection(
            required_skills
        )
    )

    missing = sorted(
        required_skills.difference(
            candidate_skills
        )
    )

    score = (
        len(matched)
        / len(required_skills)
    ) * 100

    return (
        clamp_score(score),
        matched,
        missing,
    )


# ============================================================
# PREFERRED SKILLS
# ============================================================

def calculate_preferred_skill_match(
    candidate: CandidateProfile,
    job: JobProfile,
) -> Tuple[float, List[str]]:
    """
    Preferred skills are scored separately from mandatory skills.
    """

    candidate_skills = normalize_skills(
        candidate.skills
    )

    preferred_skills = normalize_skills(
        job.preferred_skills
    )

    if not preferred_skills:
        return 0.0, []

    matched = sorted(
        candidate_skills.intersection(
            preferred_skills
        )
    )

    score = (
        len(matched)
        / len(preferred_skills)
    ) * 100

    return (
        clamp_score(score),
        matched,
    )


# ============================================================
# PROJECT RELEVANCE
# ============================================================

def calculate_project_relevance(
    candidate: CandidateProfile,
    job: JobProfile,
) -> float:
    """
    Hybrid project relevance.

    Combines:
    1. Exact technology overlap with JD skills.
    2. Semantic similarity between project content and the role.

    Best projects receive the most importance rather than forcing
    unrelated projects to lower the candidate score too much.
    """

    if not candidate.projects:
        return 0.0

    job_skills = normalize_skills(
        job.required_skills
        + job.preferred_skills
    )

    job_context_parts = []

    if job.title:
        job_context_parts.append(
            job.title
        )

    job_context_parts.extend(
        job.required_skills
    )

    job_context_parts.extend(
        job.preferred_skills
    )

    job_context_parts.extend(
        job.responsibilities
    )

    job_context = " ".join(
        job_context_parts
    )

    project_scores = []

    for project in candidate.projects:

        project_skills = normalize_skills(
            project.technologies
        )

        # ----------------------------
        # Technology overlap
        # ----------------------------

        if job_skills:
            overlapping_skills = (
                project_skills
                .intersection(job_skills)
            )

            technology_score = (
                len(overlapping_skills)
                / len(job_skills)
            ) * 100
        else:
            technology_score = 0.0

        # ----------------------------
        # Semantic relevance
        # ----------------------------

        project_text = " ".join(
            filter(
                None,
                [
                    project.name,
                    project.description,
                    " ".join(
                        project.technologies
                    ),
                ],
            )
        )

        semantic_score = (
            semantic_similarity(
                project_text,
                job_context,
            )
            if job_context
            else 0.0
        )

        # Exact technology evidence is more reliable than
        # embeddings for technical project relevance.
        hybrid_score = (
            technology_score * 0.60
            + semantic_score * 0.40
        )

        project_scores.append(
            clamp_score(
                hybrid_score
            )
        )

    if not project_scores:
        return 0.0

    project_scores.sort(
        reverse=True
    )

    # Use the two most relevant projects.
    top_projects = project_scores[:2]

    return clamp_score(
        sum(top_projects)
        / len(top_projects)
    )


# ============================================================
# EXPERIENCE
# ============================================================

def calculate_experience_relevance(
    candidate: CandidateProfile,
    job: JobProfile,
) -> float:
    """
    Evaluate work/internship relevance.

    Entry-level roles do not heavily penalize fresh graduates.
    """

    minimum_experience = (
        job.minimum_experience
    )

    if not candidate.experience:

        if (
            minimum_experience is not None
            and minimum_experience <= 0
        ):
            return 70.0

        return 0.0

    experience_text = " ".join(
        " ".join(
            filter(
                None,
                [
                    experience.company,
                    experience.role,
                    experience.description,
                ],
            )
        )
        for experience
        in candidate.experience
    )

    job_context = " ".join(
        filter(
            None,
            [
                job.title,
                " ".join(
                    job.required_skills
                ),
                " ".join(
                    job.preferred_skills
                ),
                " ".join(
                    job.responsibilities
                ),
            ],
        )
    )

    relevance = semantic_similarity(
        experience_text,
        job_context,
    )

    # Fresher/entry-level roles should recognize internships
    # as useful professional exposure.
    if (
        minimum_experience is not None
        and minimum_experience <= 0
    ):
        relevance = max(
            relevance,
            70.0,
        )

    return clamp_score(
        relevance
    )


# ============================================================
# EDUCATION
# ============================================================

def calculate_education_relevance(
    candidate: CandidateProfile,
    job: JobProfile,
) -> float:
    """
    Hybrid education evaluation.

    Degree level and relevant field are evaluated explicitly rather
    than relying entirely on embedding similarity.
    """

    if not job.education_requirements:
        return 100.0

    if not candidate.education:
        return 0.0

    candidate_text = " ".join(
        " ".join(
            filter(
                None,
                [
                    education.degree,
                    education.field_of_study,
                    education.institution,
                ],
            )
        )
        for education
        in candidate.education
    )

    job_text = " ".join(
        job.education_requirements
    )

    candidate_lower = (
        candidate_text.lower()
    )

    job_lower = (
        job_text.lower()
    )

    # ----------------------------
    # Degree-level matching
    # ----------------------------

    degree_level_score = 0.0

    bachelor_terms = [
        "bachelor",
        "b.tech",
        "btech",
        "b.e",
        "bsc",
        "b.sc",
    ]

    master_terms = [
        "master",
        "m.tech",
        "mtech",
        "m.e",
        "msc",
        "m.sc",
    ]

    job_requires_bachelor = any(
        term in job_lower
        for term in bachelor_terms
    )

    job_requires_master = any(
        term in job_lower
        for term in master_terms
    )

    candidate_has_bachelor = any(
        term in candidate_lower
        for term in bachelor_terms
    )

    candidate_has_master = any(
        term in candidate_lower
        for term in master_terms
    )

    if (
        job_requires_bachelor
        and (
            candidate_has_bachelor
            or candidate_has_master
        )
    ):
        degree_level_score = 100.0

    elif (
        job_requires_master
        and candidate_has_master
    ):
        degree_level_score = 100.0

    elif not (
        job_requires_bachelor
        or job_requires_master
    ):
        degree_level_score = 75.0

    # ----------------------------
    # Field relevance
    # ----------------------------

    field_score = semantic_similarity(
        candidate_text,
        job_text,
    )

    # Degree eligibility = 60%
    # Field/domain relevance = 40%
    education_score = (
        degree_level_score * 0.60
        + field_score * 0.40
    )

    return clamp_score(
        education_score
    )


# ============================================================
# CERTIFICATIONS
# ============================================================

def calculate_certification_score(
    candidate: CandidateProfile,
    job: JobProfile,
) -> float:
    """
    Score certification relevance against the role and required skills.
    """

    if not candidate.certifications:
        return 0.0

    certification_text = " ".join(
        candidate.certifications
    )

    job_context = " ".join(
        filter(
            None,
            [
                job.title,
                " ".join(
                    job.required_skills
                ),
                " ".join(
                    job.preferred_skills
                ),
            ],
        )
    )

    if not job_context:
        return 0.0

    score = semantic_similarity(
        certification_text,
        job_context,
    )

    return clamp_score(
        score
    )


# ============================================================
# FOCUSED SEMANTIC RESUME MATCH
# ============================================================

def build_candidate_semantic_text(
    candidate: CandidateProfile,
) -> str:
    """
    Build a clean semantic representation of the candidate.

    We intentionally avoid raw PDF noise such as phone numbers,
    URLs and formatting artifacts.
    """

    parts = []

    parts.extend(
        candidate.skills
    )

    for project in candidate.projects:
        parts.append(
            project.name
        )

        if project.description:
            parts.append(
                project.description
            )

        parts.extend(
            project.technologies
        )

    for experience in candidate.experience:

        if experience.role:
            parts.append(
                experience.role
            )

        if experience.description:
            parts.append(
                experience.description
            )

    for education in candidate.education:

        if education.degree:
            parts.append(
                education.degree
            )

        if education.field_of_study:
            parts.append(
                education.field_of_study
            )

    parts.extend(
        candidate.certifications
    )

    return " ".join(
        filter(
            None,
            parts,
        )
    )


def build_job_semantic_text(
    job: JobProfile,
) -> str:
    """
    Build a focused semantic representation of the job.
    """

    parts = []

    if job.title:
        parts.append(
            job.title
        )

    parts.extend(
        job.required_skills
    )

    parts.extend(
        job.preferred_skills
    )

    parts.extend(
        job.responsibilities
    )

    parts.extend(
        job.education_requirements
    )

    return " ".join(
        filter(
            None,
            parts,
        )
    )


def calculate_semantic_resume_match(
    candidate: CandidateProfile,
    job: JobProfile,
) -> float:
    """
    Overall semantic similarity using useful structured content
    instead of noisy PDF/JD raw text.
    """

    candidate_text = (
        build_candidate_semantic_text(
            candidate
        )
    )

    job_text = (
        build_job_semantic_text(
            job
        )
    )

    if not candidate_text or not job_text:
        return 0.0

    return clamp_score(
        semantic_similarity(
            candidate_text,
            job_text,
        )
    )


# ============================================================
# COMPLETE MATCHING PIPELINE
# ============================================================

def match_candidate_to_job(
    candidate: CandidateProfile,
    job: JobProfile,
) -> Dict:
    """
    Run complete hybrid candidate-job matching.
    """

    (
        skill_score,
        matched_skills,
        missing_skills,
    ) = calculate_skill_match(
        candidate,
        job,
    )

    (
        preferred_score,
        matched_preferred_skills,
    ) = calculate_preferred_skill_match(
        candidate,
        job,
    )

    semantic_score = (
        calculate_semantic_resume_match(
            candidate,
            job,
        )
    )

    project_score = (
        calculate_project_relevance(
            candidate,
            job,
        )
    )

    experience_score = (
        calculate_experience_relevance(
            candidate,
            job,
        )
    )

    education_score = (
        calculate_education_relevance(
            candidate,
            job,
        )
    )

    certification_score = (
        calculate_certification_score(
            candidate,
            job,
        )
    )

    return {
        "skill_score": skill_score,

        "preferred_skill_score":
            preferred_score,

        "semantic_score":
            semantic_score,

        "project_score":
            project_score,

        "experience_score":
            experience_score,

        "education_score":
            education_score,

        "certification_score":
            certification_score,

        "matched_skills":
            matched_skills,

        "missing_skills":
            missing_skills,

        "matched_preferred_skills":
            matched_preferred_skills,
    }