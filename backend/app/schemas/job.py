from typing import List, Optional

from pydantic import BaseModel, Field


class JobProfile(BaseModel):
    title: Optional[str] = None

    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)

    minimum_experience: Optional[float] = None

    education_requirements: List[str] = Field(default_factory=list)

    responsibilities: List[str] = Field(default_factory=list)

    raw_text: Optional[str] = None