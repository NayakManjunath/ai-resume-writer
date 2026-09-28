from ai_resume_writer.contracts.models import (
    CandidateProfile,
    JobDescription,
    TargetRole,
)


def _clean_value(value: str | None) -> str | None:
    """Return a normalized non-empty string or None."""
    if value is None:
        return None

    cleaned = value.strip()

    return cleaned if cleaned else None


def _extract_resume_designation(
    candidate_profile: CandidateProfile,
) -> str | None:
    """Extract a designation from structured resume experience evidence."""
    for experience_item in candidate_profile.experience:
        cleaned = _clean_value(experience_item)

        if not cleaned:
            continue

        # The first line of an experience entry is treated as the
        # candidate's available designation evidence.
        return cleaned

    return None


def resolve_target_role(
    *,
    user_designation: str | None = None,
    job_description: JobDescription | None = None,
    candidate_profile: CandidateProfile | None = None,
) -> TargetRole | None:
    """Resolve the target designation using the approved priority.

    Priority:
    1. Explicit user designation
    2. Job Description title
    3. Resume experience designation
    4. No reliable designation -> None
    """
    explicit_designation = _clean_value(user_designation)

    if explicit_designation:
        return TargetRole(
            designation=explicit_designation,
            source="user",
        )

    if job_description is not None:
        jd_title = _clean_value(job_description.title)

        if jd_title:
            return TargetRole(
                designation=jd_title,
                source="jd",
            )

    if candidate_profile is not None:
        resume_designation = _extract_resume_designation(
            candidate_profile
        )

        if resume_designation:
            return TargetRole(
                designation=resume_designation,
                source="resume",
            )

    return None