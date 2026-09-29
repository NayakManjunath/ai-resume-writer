from __future__ import annotations

from ai_resume_writer.contracts.models import (
    CandidateProfile,
    GapItem,
    InformationStatus,
    JobDescription,
)


def _normalize_skill(skill: str) -> str:
    """Normalize a skill for case-insensitive comparison."""
    return " ".join(skill.strip().lower().split())


def _unique_skills(skills: list[str]) -> list[str]:
    """Preserve original wording while removing normalized duplicates."""
    unique: list[str] = []
    seen: set[str] = set()

    for skill in skills:
        if not skill.strip():
            continue

        normalized = _normalize_skill(skill)

        if normalized in seen:
            continue

        seen.add(normalized)
        unique.append(skill)

    return unique


def _missing_skills(
    candidate_skills: list[str],
    job_skills: list[str],
) -> list[str]:
    """Return JD skills not found in the candidate's resume."""
    candidate_lookup = {
        _normalize_skill(skill)
        for skill in candidate_skills
        if skill.strip()
    }

    missing: list[str] = []

    for skill in _unique_skills(job_skills):
        if _normalize_skill(skill) not in candidate_lookup:
            missing.append(skill)

    return missing


def _build_gap_item(
    *,
    skill: str,
    category: str,
) -> GapItem:
    """Build a reviewable gap item without claiming lack of experience."""
    return GapItem(
        category=category,
        item=skill,
        reason=(
            f"{skill} appears relevant to the target role but was not found "
            f"in your resume. Have you worked with {skill}?"
        ),
        status=InformationStatus.DETECTED,
    )


def identify_missing_skills(
    *,
    candidate_profile: CandidateProfile,
    job_description: JobDescription,
) -> list[GapItem]:
    """Identify JD skills not found in the candidate's resume.

    This function reports potential gaps for user review. It does not
    determine that the candidate lacks a skill and does not add information
    to the candidate profile.
    """
    missing_required = _missing_skills(
        candidate_profile.skills,
        job_description.required_skills,
    )

    missing_preferred = _missing_skills(
        candidate_profile.skills,
        job_description.preferred_skills,
    )

    gaps: list[GapItem] = []

    for skill in missing_required:
        gaps.append(
            _build_gap_item(
                skill=skill,
                category="required_skill",
            )
        )

    for skill in missing_preferred:
        gaps.append(
            _build_gap_item(
                skill=skill,
                category="preferred_skill",
            )
        )

    return gaps