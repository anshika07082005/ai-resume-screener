from typing import List, Optional

from pydantic import BaseModel, Field


class ScoreBreakdown(BaseModel):
    skills: float
    preferred_skills: float
    semantic_similarity: float
    projects: float
    experience: float
    education: float
    certifications: float


class ScreeningResult(BaseModel):
    candidate_name: Optional[str] = None
    job_title: Optional[str] = None

    overall_score: float

    breakdown: ScoreBreakdown

    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    matched_preferred_skills: List[str] = Field(default_factory=list)

    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)

    recommendation: str