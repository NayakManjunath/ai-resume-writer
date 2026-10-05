from ai_resume_writer.contracts.models import CandidateProfile


SECTION_MAPPING = {
    "professional_summary": "PROFESSIONAL SUMMARY",
    "skills": "SKILLS",
    "experience": "EXPERIENCE",
    "projects": "PROJECTS",
    "education": "EDUCATION",
    "certifications": "CERTIFICATIONS",
}


def select_resume_sections(
    candidate_profile: CandidateProfile,
) -> list[str]:
    """Select resume sections that contain actual candidate information."""
    selected_sections: list[str] = []

    for field_name, section_name in SECTION_MAPPING.items():
        value = getattr(candidate_profile, field_name)

        if _has_content(value):
            selected_sections.append(section_name)

    return selected_sections


def _has_content(value: object) -> bool:
    """Return True when a value contains meaningful resume information."""
    if isinstance(value, str):
        return bool(value.strip())

    if isinstance(value, list):
        return any(
            isinstance(item, str) and item.strip()
            for item in value
        )

    return value is not None