from ai_resume_writer.contracts.models import (
    ResumeAnalysis,
    ResumeFormatChoice,
    ResumeImprovement,
)


def _build_information_summary(analysis: ResumeAnalysis) -> list[str]:
    """Build a factual summary from the existing candidate profile."""
    profile = analysis.candidate_profile
    summary: list[str] = []

    if profile.name:
        summary.append(f"Candidate: {profile.name}")

    if profile.professional_summary:
        summary.append("Professional summary: available.")

    if profile.skills:
        summary.append(
            f"Skills found: {', '.join(profile.skills)}."
        )

    if profile.experience:
        summary.append(
            f"Experience entries found: {len(profile.experience)}."
        )

    if profile.projects:
        summary.append(
            f"Projects found: {len(profile.projects)}."
        )

    if profile.education:
        summary.append(
            f"Education entries found: {len(profile.education)}."
        )

    if profile.certifications:
        summary.append(
            f"Certifications found: {len(profile.certifications)}."
        )

    if profile.experience_years is not None:
        summary.append(
            f"Calculated experience: {profile.experience_years:g} years."
        )

    return summary


def _build_gap_summary(analysis: ResumeAnalysis) -> list[str]:
    """Build gap and requested-information summaries from existing gaps."""
    summary: list[str] = []

    for gap in analysis.gaps:
        if gap.category == "missing_section":
            summary.append(
                f"Missing section: {gap.item}."
            )
            continue

        if gap.category == "missing_skill":
            summary.append(
                f"Potential missing skill: {gap.item}."
            )
            summary.append(gap.reason)
            continue

        if gap.category == "missing_project":
            summary.append(
                f"Potential missing project: {gap.item}."
            )
            summary.append(gap.reason)
            continue

        if gap.category == "weak_evidence":
            summary.append(
                f"Weak evidence identified: {gap.item}."
            )
            summary.append(gap.reason)
            continue

        if gap.category == "metric_opportunity":
            summary.append(
                f"Metric opportunity: {gap.item}."
            )
            summary.append(gap.reason)
            continue

        summary.append(
            f"Potential gap: {gap.item}."
        )
        summary.append(gap.reason)

    return summary


def _build_format_summary(
    format_choice: ResumeFormatChoice,
) -> str:
    if format_choice == ResumeFormatChoice.USE_TEMPLATE:
        return "Format choice: use professional ATS-friendly template."

    return "Format choice: keep existing resume format."


def build_resume_improvement_report(
    analysis: ResumeAnalysis,
    format_choice: ResumeFormatChoice,
) -> ResumeImprovement:
    """Build a deterministic resume improvement report.

    The report is derived only from existing resume analysis and the
    user's explicit format choice. It does not call an LLM or add
    unsupported candidate information.
    """
    original_profile = analysis.candidate_profile.model_copy(
        deep=True
    )

    improvement_summary: list[str] = [
        f"Target role: {analysis.target_role.designation}.",
        *_build_information_summary(analysis),
        *_build_gap_summary(analysis),
        _build_format_summary(format_choice),
    ]

    return ResumeImprovement(
        target_role=analysis.target_role,
        format_choice=format_choice,
        original_profile=original_profile,
        improved_sections={},
        improvement_summary=improvement_summary,
    )