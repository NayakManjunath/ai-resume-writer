
"""Streamlit interface for resume and Job Description input."""

import streamlit as st

from ai_resume_writer.jd.input import (
    JobDescriptionInputError,
    create_job_description,
)
from ai_resume_writer.jd.missing import (
    MISSING_JD_QUESTION,
    MissingJDDecision,
    handle_missing_jd,
)
from ai_resume_writer.resume.extractor import (
    ResumeExtractionError,
    extract_resume,
)
from ai_resume_writer.resume.uploader import (
    ResumeUploadError,
    create_resume_document,
)


def load_resume_upload(file_name: str, file_bytes: bytes):
    """Validate an uploaded resume and extract its text."""
    create_resume_document(
        file_name=file_name,
        file_bytes=file_bytes,
    )
    return extract_resume(
        file_name=file_name,
        file_bytes=file_bytes,
    )


def load_job_description(text: str):
    """Validate and create a Job Description contract."""
    return create_job_description(text=text)


def render_input_page() -> None:
    """Render the initial resume and Job Description input screen."""
    st.set_page_config(
        page_title="AI Resume Writer",
        page_icon="📄",
        layout="centered",
    )

    st.title("AI Resume Writer")
    st.write(
        "Improve your resume using your existing experience and "
        "the requirements of your target role. Your information "
        "will not be treated as permission to invent qualifications."
    )

    st.subheader("1. Upload your resume")
    uploaded_file = st.file_uploader(
        "Choose a PDF or DOCX resume",
        type=["pdf", "docx"],
        help="Upload a resume containing selectable text.",
        key="resume_upload",
    )

    st.subheader("2. Add the Job Description")
    jd_text = st.text_area(
        "Paste the complete Job Description",
        placeholder=(
            "Paste the job title, responsibilities, required skills, "
            "and qualifications here."
        ),
        height=220,
        key="jd_text",
    )

    if st.button("Validate inputs", type="primary"):
        st.session_state.pop("resume_document", None)
        st.session_state.pop("job_description", None)
        st.session_state.pop("missing_jd_handling", None)
        st.session_state["input_validation_attempted"] = True

        if uploaded_file is None:
            st.error("Please upload your resume.")
            return

        try:
            resume = load_resume_upload(
                file_name=uploaded_file.name,
                file_bytes=uploaded_file.getvalue(),
            )
        except (ResumeUploadError, ResumeExtractionError, ValueError) as exc:
            st.error(f"Unable to process the resume: {exc}")
            return

        st.session_state["resume_document"] = resume

        if jd_text.strip():
            try:
                job_description = load_job_description(jd_text)
            except (JobDescriptionInputError, ValueError) as exc:
                st.error(f"Unable to process the Job Description: {exc}")
                return

            st.session_state["job_description"] = job_description
            st.session_state["missing_jd_handling"] = None
            st.success("Resume and Job Description validated successfully.")
            st.info(
                "Both inputs are ready. Resume analysis and gap review "
                "will be connected in a later stage."
            )
        else:
            st.session_state["job_description"] = None
            st.session_state["missing_jd_handling"] = None
            st.rerun()

    # Show the explicit missing-JD decision after a valid resume is loaded.
    resume = st.session_state.get("resume_document")
    job_description = st.session_state.get("job_description")
    handling = st.session_state.get("missing_jd_handling")

    if resume is not None and job_description is None:
        st.warning(MISSING_JD_QUESTION)

        with st.form("missing_jd_decision_form"):
            decision_label = st.radio(
                "Choose how you want to continue",
                options=[
                    "No, I will provide a Job Description",
                    "Yes, continue without Job Description",
                ],
                index=0,
            )
            decision_submitted = st.form_submit_button("Confirm decision")

        if decision_submitted:
            decision = (
                MissingJDDecision.YES
                if decision_label.startswith("Yes")
                else MissingJDDecision.NO
            )

            try:
                handling = handle_missing_jd(
                    resume=resume,
                    decision=decision,
                )
            except ValueError as exc:
                st.error(str(exc))
                return

            st.session_state["missing_jd_handling"] = handling

            if handling.continue_without_jd:
                st.success(
                    "Resume accepted. Recommendations will be based on "
                    "your resume only, without Job Description-based "
                    "tailoring."
                )
                st.info(
                    "Resume analysis will be connected in a later stage."
                )
            else:
                st.info(
                    "Please add the Job Description above and validate "
                    "your inputs again."
                )

    elif handling is not None and handling.continue_without_jd:
        st.info(
            "You chose to continue without a Job Description. "
            "Recommendations must remain resume-based."
        )
