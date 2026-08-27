import re
from typing import List, Optional

from backend.app.schemas.candidate import (
    CandidateProfile,
    Education,
    Experience,
    Project,
)
from backend.utils.skills import extract_skills


# ============================================================
# SECTION CONFIGURATION
# ============================================================

SECTION_HEADINGS = [
    "education",
    "coursework / skills",
    "coursework",
    "projects",
    "internship",
    "internships",
    "experience",
    "work experience",
    "professional experience",
    "technical skills",
    "skills",
    "certifications",
    "certification",
    "extracurricular",
    "achievements",
]


# ============================================================
# GENERAL TEXT CLEANING
# ============================================================

def clean_text(text: str) -> str:
    """
    Perform basic normalization on text extracted from a resume.
    """

    if not text:
        return ""

    # Normalize bullet character
    text = text.replace("\u2022", "•")

    # Normalize tabs and repeated spaces without destroying newlines
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# ============================================================
# BASIC CONTACT INFORMATION
# ============================================================

def extract_email(text: str) -> Optional[str]:
    """
    Extract an email address and handle common PDF extraction artifacts.
    """

    matches = re.findall(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        text,
    )

    if not matches:
        return None

    email = matches[0].strip()

    # Remove non-email characters that may appear before the address
    email = re.sub(
        r"^[^A-Za-z0-9]+",
        "",
        email,
    )

    # Common artifacts introduced by PDF extraction
    artifact_prefixes = [
        "envelope",
        "envel",
        "email",
        "mail",
        "pe",
    ]

    for prefix in artifact_prefixes:
        if email.lower().startswith(prefix):
            candidate = email[len(prefix):]

            if re.fullmatch(
                r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
                candidate,
            ):
                email = candidate
                break

    return email


def extract_phone(text: str) -> Optional[str]:
    """
    Extract an Indian mobile number with or without +91.
    """

    match = re.search(
        r"(?:\+91[-\s]?)?[6-9]\d{9}",
        text,
    )

    if match:
        return match.group(0).strip()

    return None


def extract_name(text: str) -> Optional[str]:
    """
    Attempt to identify the candidate's name from the first few lines.
    """

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    for line in lines[:5]:
        lower_line = line.lower()

        if "resume" in lower_line:
            continue

        if "curriculum vitae" in lower_line:
            continue

        if "@" in line:
            continue

        if re.search(r"\d", line):
            continue

        words = line.split()

        if 2 <= len(words) <= 5:
            return line

    return None


# ============================================================
# SECTION EXTRACTION
# ============================================================

def normalize_heading(line: str) -> str:
    """
    Normalize potential resume section headings.
    """

    return re.sub(
        r"[^a-zA-Z/ &]",
        "",
        line,
    ).strip().lower()


def get_section(
    text: str,
    target_headings: List[str],
) -> str:
    """
    Extract everything belonging to a specific resume section until
    another known section heading is encountered.
    """

    lines = text.splitlines()

    normalized_targets = [
        heading.lower()
        for heading in target_headings
    ]

    start_index = None

    for index, line in enumerate(lines):
        normalized = normalize_heading(line)

        if normalized in normalized_targets:
            start_index = index + 1
            break

    if start_index is None:
        return ""

    collected = []

    for line in lines[start_index:]:
        normalized = normalize_heading(line)

        if normalized in SECTION_HEADINGS:
            break

        collected.append(line)

    return "\n".join(collected).strip()


# ============================================================
# YEAR EXTRACTION
# ============================================================

def extract_years(text: str) -> List[int]:
    """
    Extract four-digit years.

    Uses digit boundaries instead of normal word boundaries so text
    such as 'Management2022 – 2026' still returns [2022, 2026].
    """

    matches = re.findall(
        r"(?<!\d)(?:19|20)\d{2}(?!\d)",
        text,
    )

    return [int(year) for year in matches]


# ============================================================
# EDUCATION
# ============================================================

def extract_education(text: str) -> List[Education]:
    """
    Extract structured education entries.
    """

    section = get_section(
        text,
        ["education"],
    )

    if not section:
        return []

    lines = [
        line.strip()
        for line in section.splitlines()
        if line.strip()
    ]

    education: List[Education] = []

    index = 0

    while index < len(lines):
        line = lines[index]
        lower_line = line.lower()

        # ----------------------------------------------------
        # College / University
        # ----------------------------------------------------

        if any(
            keyword in lower_line
            for keyword in [
                "institute",
                "university",
                "college",
            ]
        ):
            institution = line

            degree = None
            field_of_study = None

            if index + 1 < len(lines):
                next_line = lines[index + 1]
                lower_next = next_line.lower()

                degree_keywords = [
                    "b.tech",
                    "btech",
                    "m.tech",
                    "mtech",
                    "b.sc",
                    "bsc",
                    "m.sc",
                    "msc",
                    "bachelor",
                    "master",
                    "b.e",
                    "m.e",
                ]

                if any(
                    keyword in lower_next
                    for keyword in degree_keywords
                ):
                    degree = next_line

                    if (
                        "artificial intelligence" in lower_next
                        and "machine learning" in lower_next
                    ):
                        field_of_study = (
                            "Artificial Intelligence and Machine Learning"
                        )

            years = extract_years(institution)

            start_year = (
                years[0]
                if len(years) >= 1
                else None
            )

            end_year = (
                years[1]
                if len(years) >= 2
                else None
            )

            education.append(
                Education(
                    institution=institution,
                    degree=degree,
                    field_of_study=field_of_study,
                    start_year=start_year,
                    end_year=end_year,
                )
            )

            if degree:
                index += 2
            else:
                index += 1

            continue

        # ----------------------------------------------------
        # School
        # ----------------------------------------------------

        if "school" in lower_line:
            institution = line

            degree = None
            field_of_study = None

            if index + 1 < len(lines):
                next_line = lines[index + 1]

                # Don't accidentally consume another institution
                if not any(
                    keyword in next_line.lower()
                    for keyword in [
                        "school",
                        "college",
                        "university",
                        "institute",
                    ]
                ):
                    degree = next_line

                    if "pcm" in next_line.lower():
                        field_of_study = "PCM"

            years = extract_years(institution)

            end_year = (
                years[-1]
                if years
                else None
            )

            education.append(
                Education(
                    institution=institution,
                    degree=degree,
                    field_of_study=field_of_study,
                    start_year=None,
                    end_year=end_year,
                )
            )

            if degree:
                index += 2
            else:
                index += 1

            continue

        index += 1

    return education


# ============================================================
# EXPERIENCE / INTERNSHIP
# ============================================================

def extract_experience(text: str) -> List[Experience]:
    """
    Extract internship or work-experience information.
    """

    section = get_section(
        text,
        [
            "internship",
            "internships",
            "experience",
            "work experience",
            "professional experience",
        ],
    )

    if not section:
        return []

    lines = [
        line.strip()
        for line in section.splitlines()
        if line.strip()
    ]

    if len(lines) < 2:
        return []

    company_line = lines[0]

    company_line = company_line.replace(
        "/external-link-alt",
        "",
    ).strip()

    # Example:
    # CodSoft Sept 2023 – Oct 2023

    date_match = re.search(
        r"([A-Za-z]{3,9}\s+\d{4})"
        r"\s*[–—-]\s*"
        r"([A-Za-z]{3,9}\s+\d{4})",
        company_line,
    )

    start_date = None
    end_date = None

    if date_match:
        start_date = date_match.group(1)
        end_date = date_match.group(2)

    company = re.sub(
        r"[A-Za-z]{3,9}\s+\d{4}"
        r"\s*[–—-]\s*"
        r"[A-Za-z]{3,9}\s+\d{4}",
        "",
        company_line,
    ).strip()

    role_line = lines[1]

    role = re.sub(
        r"\bRemote\b",
        "",
        role_line,
        flags=re.IGNORECASE,
    ).strip()

    description_lines = []

    for line in lines[2:]:
        cleaned = line.lstrip("•- ").strip()

        if cleaned:
            description_lines.append(cleaned)

    description = "\n".join(description_lines)

    return [
        Experience(
            company=company or "Unknown",
            role=role or "Unknown",
            start_date=start_date,
            end_date=end_date,
            description=description or None,
        )
    ]


# ============================================================
# PROJECTS
# ============================================================

def split_projects(section: str) -> List[str]:
    """
    Split the projects section into individual project blocks.
    """

    lines = [
        line.rstrip()
        for line in section.splitlines()
        if line.strip()
    ]

    blocks = []
    current = []

    for line in lines:
        is_project_title = (
            not line.lstrip().startswith("•")
            and (
                "|" in line
                or "/external-link-alt" in line
            )
        )

        if is_project_title and current:
            blocks.append(
                "\n".join(current).strip()
            )

            current = []

        current.append(line)

    if current:
        blocks.append(
            "\n".join(current).strip()
        )

    return blocks


def extract_projects(text: str) -> List[Project]:
    """
    Extract individual projects, descriptions and technologies.
    """

    section = get_section(
        text,
        ["projects"],
    )

    if not section:
        return []

    blocks = split_projects(section)

    projects: List[Project] = []

    for block in blocks:
        lines = [
            line.strip()
            for line in block.splitlines()
            if line.strip()
        ]

        if not lines:
            continue

        first_line = lines[0]

        first_line = first_line.replace(
            "/external-link-alt",
            "",
        )

        parts = first_line.split("|", 1)

        project_name = parts[0].strip()

        tech_text = (
            parts[1].strip()
            if len(parts) > 1
            else ""
        )

        description_lines = []

        for line in lines[1:]:
            cleaned = line.lstrip("•- ").strip()

            if cleaned:
                description_lines.append(cleaned)

        description = "\n".join(
            description_lines
        )

        technologies = sorted(
            extract_skills(
                f"{tech_text}\n{block}"
            )
        )

        projects.append(
            Project(
                name=project_name,
                description=description or None,
                technologies=technologies,
            )
        )

    return projects


# ============================================================
# CERTIFICATIONS
# ============================================================

def extract_certifications(text: str) -> List[str]:
    """
    Extract certifications while stopping before the next section.
    """

    section = get_section(
        text,
        [
            "certifications",
            "certification",
        ],
    )

    if not section:
        return []

    certifications = []

    for line in section.splitlines():
        cleaned = line.strip()
        cleaned = cleaned.lstrip("•- ").strip()

        if cleaned:
            certifications.append(cleaned)

    return certifications


# ============================================================
# MAIN RESUME PARSER
# ============================================================

def parse_resume(text: str) -> CandidateProfile:
    """
    Convert raw resume text into a structured CandidateProfile.
    """

    cleaned_text = clean_text(text)

    candidate = CandidateProfile(
        name=extract_name(cleaned_text),
        email=extract_email(cleaned_text),
        phone=extract_phone(cleaned_text),
        skills=sorted(
            extract_skills(cleaned_text)
        ),
        education=extract_education(cleaned_text),
        experience=extract_experience(cleaned_text),
        projects=extract_projects(cleaned_text),
        certifications=extract_certifications(cleaned_text),
        raw_text=cleaned_text,
    )

    return candidate