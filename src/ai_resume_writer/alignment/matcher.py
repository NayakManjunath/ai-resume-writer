from __future__ import annotations

import re
from dataclasses import dataclass

from ai_resume_writer.contracts.models import (
    CandidateProfile,
    JobDescription,
    TargetRole,
)


@dataclass(frozen=True)
class ResumeJDAlignment:
    """Deterministic alignment evidence between a resume and Job Description."""

    target_role: TargetRole
    job_title: str | None
    candidate_role_evidence: str | None

    matched_required_skills: list[str]
    missing_required_skills: list[str]

    matched_preferred_skills: list[str]
    missing_preferred_skills: list[str]

    resume_only_skills: list[str]

    required_experience_years: float | None
    candidate_experience_years: float | None
    meets_experience_requirement: bool | None

    candidate_projects: list[str]
    candidate_experience: list[str]


def _normalize_skill(skill: str) -> str:
    """Normalize a skill for deterministic comparison."""
    return " ".join(skill.strip().lower().split())


def _unique_skills(skills: list[str]) -> list[str]:
    """Preserve original values while removing duplicates by normalized value."""
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

def _match_skills(
    candidate_skills: list[str],
    job_skills: list[str],
) -> tuple[list[str], list[str]]:
    """Return candidate-matched and missing JD skills."""
    candidate_values = _unique_skills(candidate_skills)
    job_values = _unique_skills(job_skills)

    candidate_lookup = {
        _normalize_skill(skill): skill
        for skill in candidate_values
    }

    matched: list[str] = []
    missing: list[str] = []

    for job_skill in job_values:
        normalized = _normalize_skill(job_skill)

        if normalized in candidate_lookup:
            matched.append(candidate_lookup[normalized])
        else:
            missing.append(job_skill)

    return matched, missing


def _find_resume_only_skills(
    candidate_skills: list[str],
    required_skills: list[str],
    preferred_skills: list[str],
) -> list[str]:
    """Return resume skills absent from both JD skill groups."""
    candidate_values = _unique_skills(candidate_skills)

    job_skill_values = _unique_skills(
        required_skills + preferred_skills
    )

    job_lookup = {
        _normalize_skill(skill)
        for skill in job_skill_values
    }

    return [
        skill
        for skill in candidate_values
        if _normalize_skill(skill) not in job_lookup
    ]


_EXPERIENCE_PATTERNS = (
    re.compile(
        r"\b(?:minimum\s+)?(\d+(?:\.\d+)?)\s*\+?\s*years?"
        r"(?:\s+of\s+(?:professional\s+)?experience)?",
        re.IGNORECASE,
    ),
)


def _extract_required_experience_years(
    job_description: JobDescription,
) -> float | None:
    """Extract an explicit experience requirement from JD text."""
    text = job_description.raw_text

    for pattern in _EXPERIENCE_PATTERNS:
        match = pattern.search(text)
        if match:
            return float(match.group(1))

    return None


def _compare_experience(
    candidate_years: float | None,
    required_years: float | None,
) -> bool | None:
    """Compare candidate experience only when both values are known."""
    if required_years is None or candidate_years is None:
        return None

    return candidate_years >= required_years


def _candidate_role_evidence(
    candidate_profile: CandidateProfile,
) -> str | None:
    """Return the first available raw employment evidence."""
    for experience_item in candidate_profile.experience:
        cleaned = experience_item.strip()
        if cleaned:
            return cleaned

    return None


def align_resume_with_job_description(
    *,
    candidate_profile: CandidateProfile,
    job_description: JobDescription,
    target_role: TargetRole,
) -> ResumeJDAlignment:
    """Build deterministic resume/JD alignment evidence.

    This function reports evidence only. It does not recommend adding
    information, rewrite resume content, or infer unsupported qualifications.
    """
    matched_required, missing_required = _match_skills(
        candidate_profile.skills,
        job_description.required_skills,
    )

    matched_preferred, missing_preferred = _match_skills(
        candidate_profile.skills,
        job_description.preferred_skills,
    )

    resume_only = _find_resume_only_skills(
        candidate_profile.skills,
        job_description.required_skills,
        job_description.preferred_skills,
    )

    required_experience_years = _extract_required_experience_years(
        job_description
    )

    return ResumeJDAlignment(
        target_role=target_role,
        job_title=job_description.title,
        candidate_role_evidence=_candidate_role_evidence(candidate_profile),
        matched_required_skills=matched_required,
        missing_required_skills=missing_required,
        matched_preferred_skills=matched_preferred,
        missing_preferred_skills=missing_preferred,
        resume_only_skills=resume_only,
        required_experience_years=required_experience_years,
        candidate_experience_years=candidate_profile.experience_years,
        meets_experience_requirement=_compare_experience(
            candidate_profile.experience_years,
            required_experience_years,
        ),
        candidate_projects=list(candidate_profile.projects),
        candidate_experience=list(candidate_profile.experience),
    )