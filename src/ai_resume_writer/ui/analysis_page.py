
"""Streamlit interface for resume analysis and gap review."""

import streamlit as st

from ai_resume_writer.alignment.matcher import (
    ResumeJDAlignment,
    align_resume_with_job_description,
)
from ai_resume_writer.contracts.models import (
    CandidateProfile,
    JobDescription,
    ResumeAnalysis,
)
from ai_resume_writer.gap_analysis.metrics import (
    identify_metric_opportunities,
)
from ai_resume_writer.gap_analysis.projects_sections import (
    identify_missing_projects_and_sections,
)
from ai_resume_writer.gap_analysis.skills import (
    identify_missing_skills,
)
from ai_resume_writer.gap_analysis.weak_evidence import (
    identify_weak_evidence,
)
from ai_resume_writer.jd.parser import parse_job_description
from ai_resume_writer.resume.parser import parse_resume_information
from ai_resume_writer.role.resolver import resolve_target_role
from ai_resume_writer.contracts.models import ResumeFormatChoice
from ai_resume_writer.formatting.decision import resolve_format_choice

def build_resume_analysis(
    *,
    resume,
    job_description: JobDescription | None,
    user_designation: str | None = None,
) -> tuple[ResumeAnalysis, ResumeJDAlignment | None]:
    """Build a reviewable analysis without inventing candidate information."""

    candidate_profile: CandidateProfile = parse_resume_information(resume)

    parsed_jd = (
        parse_job_description(job_description)
        if job_description is not None
        else None
    )

    target_role = resolve_target_role(
        user_designation=user_designation,
        job_description=parsed_jd,
        candidate_profile=candidate_profile,
    )

    if target_role is None:
        raise ValueError(
            "A target designation could not be determined. "
            "Enter the designation you want to target."
        )

    gaps = []

    # Resume-only checks remain useful even when no JD is supplied.
    gaps.extend(identify_weak_evidence(candidate_profile))
    gaps.extend(identify_metric_opportunities(candidate_profile))

    alignment = None

    if parsed_jd is not None:
        alignment = align_resume_with_job_description(
            candidate_profile=candidate_profile,
            job_description=parsed_jd,
            target_role=target_role,
        )

        gaps.extend(
            identify_missing_skills(
                candidate_profile=candidate_profile,
                job_description=parsed_jd,
            )
        )
        gaps.extend(
            identify_missing_projects_and_sections(
                candidate_profile,
                parsed_jd,
            )
        )

    analysis = ResumeAnalysis(
        target_role=target_role,
        candidate_profile=candidate_profile,
        gaps=gaps,
    )

    return analysis, alignment


def _show_list(title: str, items: list[str]) -> None:
    """Display a list without inventing fallback values."""
    st.markdown(f"**{title}**")

    if items:
        for item in items:
            st.markdown(f"- {item}")
    else:
        st.caption("No information detected in this category.")


def _render_candidate_profile(profile: CandidateProfile) -> None:
    st.subheader("Candidate profile")

    if profile.name:
        st.write(f"**Name:** {profile.name}")

    if profile.professional_summary:
        st.markdown("**Professional summary**")
        st.write(profile.professional_summary)

    _show_list("Skills", profile.skills)
    _show_list("Experience", profile.experience)
    _show_list("Projects", profile.projects)
    _show_list("Education", profile.education)
    _show_list("Certifications", profile.certifications)


def _render_alignment(alignment: ResumeJDAlignment) -> None:
    st.subheader("Resume and Job Description alignment")

    left, right = st.columns(2)

    with left:
        st.markdown("**Required skills found**")
        _show_list("Matched", alignment.matched_required_skills)
        _show_list("Not found in resume", alignment.missing_required_skills)

    with right:
        st.markdown("**Preferred skills found**")
        _show_list("Matched", alignment.matched_preferred_skills)
        _show_list("Not found in resume", alignment.missing_preferred_skills)

    _show_list("Other resume skills", alignment.resume_only_skills)

    st.markdown("**Experience requirement**")

    required = alignment.required_experience_years
    candidate = alignment.candidate_experience_years

    if required is None:
        st.info("No explicit experience requirement was detected in the JD.")
    elif candidate is None:
        st.info(
            f"The JD mentions {required:g} years of experience, "
            "but the candidate's total experience has not been calculated."
        )
    else:
        st.write(f"JD requirement: {required:g} years")
        st.write(f"Resume experience: {candidate:g} years")

        if alignment.meets_experience_requirement is True:
            st.success("The available experience value meets the requirement.")
        else:
            st.warning(
                "The available experience value is below the requirement."
            )


def _render_gaps(analysis: ResumeAnalysis) -> None:
    st.subheader("Gap review")
    st.caption(
        "These are review prompts, not claims that you lack a skill or "
        "experience. Nothing is added to your resume automatically."
    )

    if not analysis.gaps:
        st.success("No review items were detected by the current checks.")
        return

    category_labels = {
        "required_skill": "Required skill not found",
        "preferred_skill": "Preferred skill not found",
        "missing_project": "Potential missing project",
        "missing_section": "Potential missing section",
        "weak_evidence": "Experience or project needs more detail",
        "metric_opportunity": "Potential achievement metric",
    }

    for index, gap in enumerate(analysis.gaps, start=1):
        label = category_labels.get(gap.category, gap.category.replace("_", " ").title())

        with st.expander(f"{index}. {label}: {gap.item}"):
            st.write(gap.reason)
            st.caption(f"Review status: {gap.status.value}")


def render_format_selection() -> None:
    """Collect and retain the user's explicit format preference."""

    st.divider()
    st.header("4. Resume format selection")

    st.write("Would you like to change your resume format?")

    choice = st.radio(
        "Choose your preferred format",
        options=[
            "No, keep my existing format",
            "Yes, use the professional template",
        ],
        index=0,
        key="format_selection_radio",
    )

    if st.button(
        "Confirm format",
        type="primary",
        key="confirm_format_selection",
    ):
        change_format = choice.startswith("Yes")
        format_choice = resolve_format_choice(change_format)

        st.session_state["resume_format_choice"] = format_choice

        if format_choice == ResumeFormatChoice.KEEP_EXISTING:
            st.success(
                "Existing format selected. The app will preserve the "
                "format as closely as technically possible. Existing "
                "format preservation currently supports DOCX only."
            )
        else:
            st.success(
                "Professional template selected. The built-in template "
                "will be used in the document-generation stage."
            )

    saved_choice = st.session_state.get("resume_format_choice")

    if saved_choice == ResumeFormatChoice.KEEP_EXISTING:
        st.caption("Confirmed selection: Keep existing format.")
    elif saved_choice == ResumeFormatChoice.USE_TEMPLATE:
        st.caption("Confirmed selection: Professional template.")

def render_analysis_page(
    *,
    resume,
    job_description: JobDescription | None,
) -> None:
    """Render and retain the analysis results in the current session."""

    st.divider()
    st.header("3. Resume analysis and gap review")

    if job_description is None:
        st.info(
            "Resume-only analysis is selected. Skill matching and "
            "JD-based gap checks will not run without a Job Description."
        )

    designation = st.text_input(
        "Target designation (optional)",
        key="analysis_target_designation",
        placeholder="For example, Data Scientist",
        help=(
            "An entered designation takes priority over the JD title "
            "and the designation detected from the resume."
        ),
    )

    if st.button("Analyze resume", type="primary", key="run_resume_analysis"):
        try:
            analysis, alignment = build_resume_analysis(
                resume=resume,
                job_description=job_description,
                user_designation=designation or None,
            )
        except (ValueError, TypeError) as exc:
            st.session_state.pop("resume_analysis", None)
            st.session_state.pop("resume_alignment", None)
            st.error(f"Unable to complete analysis: {exc}")
        else:
            st.session_state["resume_analysis"] = analysis
            st.session_state["resume_alignment"] = alignment

    analysis = st.session_state.get("resume_analysis")
    alignment = st.session_state.get("resume_alignment")

    if analysis is None:
        return

    st.success("Resume analysis completed.")

    st.subheader("Target role")
    st.write(f"**Designation:** {analysis.target_role.designation}")
    st.caption(f"Resolved from: {analysis.target_role.source}")

    _render_candidate_profile(analysis.candidate_profile)

    if alignment is not None:
        _render_alignment(alignment)

    _render_gaps(analysis)
    render_format_selection()

    