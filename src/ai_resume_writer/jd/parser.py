from ai_resume_writer.contracts.models import JobDescription


class JobDescriptionParsingError(ValueError):
    """Raised when a Job Description cannot be parsed."""


SECTION_ALIASES = {
    "required skills": "required_skills",
    "required technical skills": "required_skills",
    "must have skills": "required_skills",
    "requirements": "required_skills",
    "preferred skills": "preferred_skills",
    "preferred technical skills": "preferred_skills",
    "nice to have": "preferred_skills",
    "nice-to-have": "preferred_skills",
}


def _normalize_heading(value: str) -> str:
    return value.strip().lower().rstrip(":")


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


def _extract_items(lines: list[str]) -> list[str]:
    items: list[str] = []

    for line in lines:
        cleaned = line.strip("•*- \t")

        if not cleaned:
            continue

        # Support simple comma-separated skill lists.
        parts = [part.strip() for part in cleaned.split(",")]

        for part in parts:
            if part:
                items.append(part)

    return items


def _extract_title(text: str, existing_title: str | None) -> str | None:
    if existing_title and existing_title.strip():
        return existing_title.strip()

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    if not lines:
        return None

    first_line = lines[0]

    if _normalize_heading(first_line) in SECTION_ALIASES:
        return None

    return first_line


def parse_job_description(
    job_description: JobDescription,
) -> JobDescription:
    if not job_description.raw_text.strip():
        raise JobDescriptionParsingError(
            "Job Description must contain text before parsing."
        )

    sections = _split_sections(job_description.raw_text)

    required_skills = _extract_items(
        sections.get("required_skills", [])
    )

    preferred_skills = _extract_items(
        sections.get("preferred_skills", [])
    )

    title = _extract_title(
        job_description.raw_text,
        job_description.title,
    )

    return JobDescription(
        raw_text=job_description.raw_text,
        title=title,
        required_skills=required_skills,
        preferred_skills=preferred_skills,
    )
