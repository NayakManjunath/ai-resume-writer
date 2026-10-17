
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

from ai_resume_writer.resume.workflow import (
    InputOrder,
    WorkflowState,
    is_workflow_ready,
    resolve_input_order,
    resolve_workflow_state,
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
    """Render the input screen with persistent sequential input handling."""
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

    # Initialize persistent state once per user session.
    st.session_state.setdefault("resume_document", None)
    st.session_state.setdefault("job_description", None)
    st.session_state.setdefault("missing_jd_handling", None)
    st.session_state.setdefault("input_order", None)
    st.session_state.setdefault("workflow_state", None)

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
        # Update the resume only when a new upload is provided.
        if uploaded_file is not None:
            try:
                resume = load_resume_upload(
                    file_name=uploaded_file.name,
                    file_bytes=uploaded_file.getvalue(),
                )
                st.session_state["resume_document"] = resume
            except (ResumeUploadError, ResumeExtractionError, ValueError) as exc:
                st.error(f"Unable to process the resume: {exc}")
                return

        # Update or clear the JD according to the current text area.
        if jd_text.strip():
            try:
                job_description = load_job_description(jd_text)
                st.session_state["job_description"] = job_description
            except (JobDescriptionInputError, ValueError) as exc:
                st.error(f"Unable to process the Job Description: {exc}")
                return
        else:
            st.session_state["job_description"] = None

        resume = st.session_state["resume_document"]
        job_description = st.session_state["job_description"]

        if resume is None and job_description is None:
            st.error("Please upload a resume or provide a Job Description.")
            st.session_state["input_order"] = None
            st.session_state["workflow_state"] = (
                WorkflowState.WAITING_FOR_RESUME
            )
            return

        # Resolve the order and state using the existing workflow logic.
        st.session_state["input_order"] = resolve_input_order(
            resume=resume,
            job_description=job_description,
        )
        st.session_state["workflow_state"] = resolve_workflow_state(
            resume=resume,
            job_description=job_description,
        )

        # A new or updated input requires a fresh missing-JD decision.
        st.session_state["missing_jd_handling"] = None

    resume = st.session_state["resume_document"]
    job_description = st.session_state["job_description"]
    input_order = st.session_state["input_order"]
    workflow_state = st.session_state["workflow_state"]

    if resume is not None:
        st.success(f"Resume retained: {resume.file_name}")

    if job_description is not None:
        st.success("Job Description retained.")

    if workflow_state == WorkflowState.WAITING_FOR_RESUME:
        st.info(
            "Job Description received. Upload your resume and select "
            "'Validate inputs' to continue."
        )

    elif workflow_state == WorkflowState.WAITING_FOR_JD:
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
                    "your resume only, without JD-based tailoring."
                )
            else:
                st.info(
                    "Add the Job Description above and validate your "
                    "inputs again."
                )

    elif workflow_state == WorkflowState.READY_FOR_ANALYSIS:
        if is_workflow_ready(
            resume=resume,
            job_description=job_description,
        ):
            st.success("Both inputs are validated and ready for analysis.")

            if input_order == InputOrder.RESUME_FIRST:
                st.caption("Input order: resume first.")
            elif input_order == InputOrder.JD_FIRST:
                st.caption("Input order: Job Description first.")
            else:
                st.caption("Input order: both supplied together.")

            st.info(
                "Analysis and gap review will be connected in a later stage."
            )

    handling = st.session_state["missing_jd_handling"]
    if (
        handling is not None
        and handling.continue_without_jd
        and job_description is None
    ):
        st.info(
            "You chose to continue without a Job Description. "
            "Recommendations must remain resume-based."
        )
