import re
from typing import List, Optional

from backend.app.schemas.job import JobProfile
from backend.utils.skills import extract_skills


# ============================================================
# SECTION DEFINITIONS
# ============================================================

SECTION_PATTERNS = {
    "about": [
        "about the role",
        "about",
        "job description",
    ],

    "responsibilities": [
        "responsibilities",
        "roles and responsibilities",
        "key responsibilities",
        "job responsibilities",
        "what you'll do",
        "what you will do",
    ],

    "required": [
        "required skills",
        "skills required",
        "requirements",
        "minimum qualifications",
        "basic qualifications",
        "required qualifications",
    ],

    "preferred": [
        "preferred skills",
        "preferred qualifications",
        "good to have",
        "nice to have",
        "bonus skills",
        "desired qualifications",
    ],

    "qualifications": [
        "qualifications",
        "education",
        "educational qualifications",
        "academic qualifications",
    ],

    "experience": [
        "experience",
        "experience required",
        "work experience",
    ],
}


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_jd_text(text: str) -> str:
    if not text:
        return ""

    text = text.replace("\u2022", "-")
    text = text.replace("–", "-")
    text = text.replace("—", "-")

    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    return text.strip()


# ============================================================
# JOB TITLE
# ============================================================

def extract_job_title(
    text: str,
) -> Optional[str]:

    match = re.search(
        r"(?i)job\s*title\s*:\s*(.+?)(?="
        r"\n|about\s+the\s+role|responsibilities|"
        r"required\s+skills|preferred\s+skills|"
        r"qualifications|experience|$)",
        text,
    )

    if match:
        title = match.group(1).strip()

        if title:
            return title[:150]

    patterns = [
        r"(?i)position\s*:\s*([^\n]+)",
        r"(?i)role\s*:\s*([^\n]+)",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
        )

        if match:
            return match.group(1).strip()[:150]

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    for line in lines[:5]:
        if any(
            keyword in line.lower()
            for keyword in [
                "engineer",
                "developer",
                "analyst",
                "scientist",
                "intern",
                "consultant",
            ]
        ):
            return line[:150]

    return None


# ============================================================
# SECTION HELPERS
# ============================================================

def _all_heading_names() -> List[str]:
    headings = []

    for values in SECTION_PATTERNS.values():
        headings.extend(values)

    return headings


def extract_section(
    text: str,
    section_name: str,
) -> str:

    headings = SECTION_PATTERNS.get(
        section_name,
        [],
    )

    if not headings:
        return ""

    all_headings = _all_heading_names()

    current_pattern = "|".join(
        re.escape(heading)
        for heading in sorted(
            headings,
            key=len,
            reverse=True,
        )
    )

    stopping_headings = [
        heading
        for heading in all_headings
        if heading not in headings
    ]

    stop_pattern = "|".join(
        re.escape(heading)
        for heading in sorted(
            stopping_headings,
            key=len,
            reverse=True,
        )
    )

    pattern = (
        rf"(?is)(?:{current_pattern})\s*:?\s*"
        rf"(.*?)"
        rf"(?=(?:{stop_pattern})\s*:|$)"
    )

    match = re.search(
        pattern,
        text,
    )

    if not match:
        return ""

    return match.group(1).strip()


# ============================================================
# EXPERIENCE
# ============================================================

def extract_minimum_experience(
    text: str,
) -> Optional[float]:

    experience_section = extract_section(
        text,
        "experience",
    )

    search_text = (
        experience_section
        if experience_section
        else text
    )

    patterns = [
        r"(?i)(\d+(?:\.\d+)?)\s*[-]\s*(\d+(?:\.\d+)?)\s*years?",
        r"(?i)(\d+(?:\.\d+)?)\+\s*years?",
        r"(?i)(?:minimum|at least)\s*(\d+(?:\.\d+)?)\s*years?",
        r"(?i)(\d+(?:\.\d+)?)\s*years?\s+of\s+experience",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            search_text,
        )

        if match:
            return float(
                match.group(1)
            )

    lower = search_text.lower()

    if any(
        phrase in lower
        for phrase in [
            "fresher",
            "fresh graduate",
            "fresh graduates",
            "recent graduate",
            "entry level",
            "entry-level",
        ]
    ):
        return 0.0

    return None


# ============================================================
# REQUIRED SKILLS
# ============================================================

def extract_required_skills(
    text: str,
) -> List[str]:

    section = extract_section(
        text,
        "required",
    )

    if not section:
        return []

    return sorted(
        set(
            extract_skills(section)
        )
    )


# ============================================================
# PREFERRED SKILLS
# ============================================================

def extract_preferred_skills(
    text: str,
) -> List[str]:

    section = extract_section(
        text,
        "preferred",
    )

    if not section:
        return []

    return sorted(
        set(
            extract_skills(section)
        )
    )


# ============================================================
# EDUCATION
# ============================================================

def extract_education_requirements(
    text: str,
) -> List[str]:

    section = extract_section(
        text,
        "qualifications",
    )

    search_text = (
        section
        if section
        else text
    )

    requirements = []

    patterns = [
        r"(?i)bachelor(?:'s)?[^.\n]*",
        r"(?i)b\.?\s*tech[^.\n]*",
        r"(?i)b\.?\s*e\.?[^.\n]*",
        r"(?i)master(?:'s)?[^.\n]*",
        r"(?i)m\.?\s*tech[^.\n]*",
        r"(?i)degree\s+in[^.\n]*",
    ]

    for pattern in patterns:
        matches = re.findall(
            pattern,
            search_text,
        )

        for item in matches:
            cleaned = item.strip(
                " -•,.:"
            )

            if not cleaned:
                continue

            duplicate = False

            for existing in requirements:
                if (
                    cleaned.lower() == existing.lower()
                    or cleaned.lower() in existing.lower()
                    or existing.lower() in cleaned.lower()
                ):
                    duplicate = True
                    break

            if not duplicate:
                requirements.append(
                    cleaned
                )

    return requirements


# ============================================================
# RESPONSIBILITIES
# ============================================================

def extract_responsibilities(
    text: str,
) -> List[str]:

    section = extract_section(
        text,
        "responsibilities",
    )

    if not section:
        return []

    items = re.split(
        r"(?:\n\s*[-•]\s*|\n+|(?<!\w)-\s+)",
        section,
    )

    responsibilities = []

    for item in items:
        cleaned = item.strip(
            " -•\n\t"
        )

        if len(cleaned) >= 10:
            responsibilities.append(
                cleaned
            )

    return responsibilities


# ============================================================
# MAIN JD PARSER
# ============================================================

def parse_job_description(
    text: str,
) -> JobProfile:

    cleaned_text = clean_jd_text(
        text
    )

    required_skills = extract_required_skills(
        cleaned_text
    )

    preferred_skills = extract_preferred_skills(
        cleaned_text
    )

    preferred_set = set(
        preferred_skills
    )

    required_skills = [
        skill
        for skill in required_skills
        if skill not in preferred_set
    ]

    return JobProfile(
        title=extract_job_title(
            cleaned_text
        ),

        required_skills=required_skills,

        preferred_skills=preferred_skills,

        minimum_experience=extract_minimum_experience(
            cleaned_text
        ),

        education_requirements=extract_education_requirements(
            cleaned_text
        ),

        responsibilities=extract_responsibilities(
            cleaned_text
        ),

        raw_text=cleaned_text,
    )