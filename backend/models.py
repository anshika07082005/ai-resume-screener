from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)

from backend.database import Base


# ============================================================
# USER
# ============================================================

class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    email = Column(
        String,
        unique=True,
        index=True,
        nullable=False,
    )

    password = Column(
        String,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )


# ============================================================
# JOB
# ============================================================

class Job(Base):
    __tablename__ = "jobs"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
    )

    title = Column(
        String,
        nullable=True,
    )

    description = Column(
        Text,
        nullable=False,
    )

    required_skills = Column(
        Text,
        nullable=True,
    )

    preferred_skills = Column(
        Text,
        nullable=True,
    )

    minimum_experience = Column(
        Float,
        nullable=True,
    )

    education_requirements = Column(
        Text,
        nullable=True,
    )

    responsibilities = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )


# ============================================================
# CANDIDATE
# ============================================================

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
    )

    name = Column(
        String,
        nullable=True,
    )

    email = Column(
        String,
        nullable=True,
    )

    phone = Column(
        String,
        nullable=True,
    )

    skills = Column(
        Text,
        nullable=True,
    )

    education = Column(
        Text,
        nullable=True,
    )

    experience = Column(
        Text,
        nullable=True,
    )

    projects = Column(
        Text,
        nullable=True,
    )

    certifications = Column(
        Text,
        nullable=True,
    )

    raw_text = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )


# ============================================================
# SCREENING RESULT
# ============================================================

class ScreeningResult(Base):
    __tablename__ = "screening_results"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
    )

    candidate_id = Column(
        Integer,
        ForeignKey("candidates.id"),
        nullable=True,
    )

    job_id = Column(
        Integer,
        ForeignKey("jobs.id"),
        nullable=True,
    )

    candidate_name = Column(
        String,
        nullable=True,
    )

    job_title = Column(
        String,
        nullable=True,
    )

    overall_score = Column(
        Float,
        nullable=False,
        default=0.0,
    )

    skill_score = Column(
        Float,
        nullable=False,
        default=0.0,
    )

    preferred_skill_score = Column(
        Float,
        nullable=False,
        default=0.0,
    )

    semantic_score = Column(
        Float,
        nullable=False,
        default=0.0,
    )

    project_score = Column(
        Float,
        nullable=False,
        default=0.0,
    )

    experience_score = Column(
        Float,
        nullable=False,
        default=0.0,
    )

    education_score = Column(
        Float,
        nullable=False,
        default=0.0,
    )

    certification_score = Column(
        Float,
        nullable=False,
        default=0.0,
    )

    matched_skills = Column(
        Text,
        nullable=True,
    )

    missing_skills = Column(
        Text,
        nullable=True,
    )

    matched_preferred_skills = Column(
        Text,
        nullable=True,
    )

    strengths = Column(
        Text,
        nullable=True,
    )

    weaknesses = Column(
        Text,
        nullable=True,
    )

    recommendation = Column(
        String,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )