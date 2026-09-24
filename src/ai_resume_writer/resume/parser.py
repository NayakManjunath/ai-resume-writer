from ai_resume_writer.contracts.models import CandidateProfile, ResumeDocument


class ResumeInformationParsingError(ValueError):
    """Raised when resume information cannot be parsed."""


SECTION_ALIASES = {
    "summary": "professional_summary",
    "professional summary": "professional_summary",
    "objective": "professional_summary",
    "skills": "skills",
    "technical skills": "skills",
    "projects": "projects",
    "experience": "experience",
    "work experience": "experience",
    "professional experience": "experience",
    "education": "education",
    "certifications": "certifications",
}


def _normalize_heading(value: str) -> str:
    return value.strip().lower()


def _split_sections(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current_section: str | None = None

    for line in text.splitlines():
        cleaned = line.strip()

        if not cleaned:
            continue

        normalized = _normalize_heading(cleaned)

        if normalized in SECTION_ALIASES:
            current_section = SECTION_ALIASES[normalized]
            sections.setdefault(current_section, [])
            continue

        if current_section is not None:
            sections[current_section].append(cleaned)

    return sections


def _extract_name(text: str) -> str | None:
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    if not lines:
        return None

    first_line = lines[0]

    if first_line.lower() in SECTION_ALIASES:
        return None

    return first_line


def _extract_list_items(lines: list[str]) -> list[str]:
    items: list[str] = []

    for line in lines:
        cleaned = line.strip("•*- \t")

        if cleaned:
            items.append(cleaned)

    return items


def parse_resume_information(
    resume: ResumeDocument,
) -> CandidateProfile:
    if not resume.raw_text.strip():
        raise ResumeInformationParsingError(
            "Resume must contain extracted text before information parsing."
        )

    sections = _split_sections(resume.raw_text)

    summary_lines = sections.get("professional_summary", [])
    skills_lines = sections.get("skills", [])
    projects_lines = sections.get("projects", [])
    experience_lines = sections.get("experience", [])
    education_lines = sections.get("education", [])
    certification_lines = sections.get("certifications", [])

    professional_summary = (
        " ".join(summary_lines)
        if summary_lines
        else None
    )

    return CandidateProfile(
        name=_extract_name(resume.raw_text),
        professional_summary=professional_summary,
        skills=_extract_list_items(skills_lines),
        projects=_extract_list_items(projects_lines),
        experience=_extract_list_items(experience_lines),
        experience_years=None,
        education=_extract_list_items(education_lines),
        certifications=_extract_list_items(certification_lines),
    )