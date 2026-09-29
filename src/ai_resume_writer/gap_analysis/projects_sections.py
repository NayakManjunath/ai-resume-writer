from ai_resume_writer.contracts.models import (
    CandidateProfile,
    GapItem,
    InformationStatus,
    JobDescription,
)


PROJECT_EVIDENCE_PATTERNS = (
    "project",
    "projects",
    "project experience",
    "portfolio project",
    "portfolio projects",
)

SECTION_EVIDENCE = {
    "professional summary": (
        "professional summary",
        "summary",
    ),
}


def _contains_project_evidence(text: str) -> bool:
    normalized_text = text.lower()
    return any(
        pattern in normalized_text
        for pattern in PROJECT_EVIDENCE_PATTERNS
    )


def _contains_section_evidence(text: str, section: str) -> bool:
    normalized_text = text.lower()
    return any(
        pattern in normalized_text
        for pattern in SECTION_EVIDENCE.get(section, ())
    )


def _build_missing_project_gap() -> GapItem:
    return GapItem(
        category="missing_project",
        item="Projects",
        reason=(
            "Project experience appears relevant to the target role but "
            "was not found in your resume. Do you have a relevant project "
            "you would like to include?"
        ),
        status=InformationStatus.DETECTED,
    )


def _build_missing_section_gap(section: str) -> GapItem:
    return GapItem(
        category="missing_section",
        item=section,
        reason=(
            f"{section} appears relevant to the target role but was not "
            f"found in your resume. Do you have information you would "
            f"like to include in this section?"
        ),
        status=InformationStatus.DETECTED,
    )


def identify_missing_projects_and_sections(
    candidate_profile: CandidateProfile,
    job_description: JobDescription,
) -> list[GapItem]:
    """Identify explicitly evidenced missing projects and resume sections.

    This function does not invent projects, skills, qualifications, or
    resume content. It only creates reviewable gaps when the JD explicitly
    contains project or section evidence.
    """
    gaps: list[GapItem] = []
    jd_text = job_description.raw_text or ""

    if _contains_project_evidence(jd_text) and not candidate_profile.projects:
        gaps.append(_build_missing_project_gap())

    if (
        _contains_section_evidence(
            jd_text,
            "professional summary",
        )
        and not candidate_profile.professional_summary
    ):
        gaps.append(_build_missing_section_gap("Professional Summary"))

    return gaps
