from ai_resume_writer.jd.input import create_job_description
from ai_resume_writer.jd.missing import (
    MissingJDDecision,
    handle_missing_jd,
)
from ai_resume_writer.resume.extractor import extract_resume
from ai_resume_writer.resume.uploader import create_resume_document
from ai_resume_writer.resume.workflow import (
    InputOrder,
    WorkflowState,
    is_workflow_ready,
    resolve_input_order,
    resolve_workflow_state,
)


def test_complete_resume_and_jd_pipeline():
    resume_bytes = (
        b"%PDF-1.4\n"
        b"John Doe\n"
        b"Data Scientist\n"
        b"Skills\n"
        b"Python SQL Machine Learning\n"
        b"Experience\n"
        b"Data Scientist\n"
    )
from pathlib import Path


FIXTURE_DIR = Path(__file__).parent / "fixtures"


def test_complete_resume_and_jd_pipeline():
    resume_path = FIXTURE_DIR / "sample_resume.pdf"
    resume_bytes = resume_path.read_bytes()

    # 2.1 Resume upload
    uploaded_resume = create_resume_document(
        file_name="sample_resume.pdf",
        file_bytes=resume_bytes,
    )

    assert uploaded_resume.file_type == "pdf"

    # 2.2 Resume extraction
    extracted_resume = extract_resume(
        file_name=uploaded_resume.file_name,
        file_bytes=resume_bytes,
    )

    assert extracted_resume.raw_text
    assert extracted_resume.sections

    # 2.3 Job Description
    job_description = create_job_description(
        text="""
        Data Scientist

        Required Skills:
        Python, SQL, Machine Learning
        """,
        title="Data Scientist",
    )

    assert job_description.title == "Data Scientist"
    assert job_description.raw_text

    # 2.4 Input ordering
    input_order = resolve_input_order(
        resume=extracted_resume,
        job_description=job_description,
    )

    workflow_state = resolve_workflow_state(
        resume=extracted_resume,
        job_description=job_description,
    )

    assert input_order == InputOrder.BOTH
    assert workflow_state == WorkflowState.READY_FOR_ANALYSIS

    assert is_workflow_ready(
        resume=extracted_resume,
        job_description=job_description,
    ) is True

    # 2.3 Job Description input
    job_description = create_job_description(
        text="""
        Data Scientist

        Required Skills:
        Python, SQL, Machine Learning
        """,
        title="Data Scientist",
    )

    assert job_description.title == "Data Scientist"
    assert "Python" in job_description.raw_text

    # 2.4 Flexible input ordering
    input_order = resolve_input_order(
        resume=uploaded_resume,
        job_description=job_description,
    )

    workflow_state = resolve_workflow_state(
        resume=uploaded_resume,
        job_description=job_description,
    )

    assert input_order == InputOrder.BOTH
    assert workflow_state == WorkflowState.READY_FOR_ANALYSIS
    assert is_workflow_ready(
        resume=uploaded_resume,
        job_description=job_description,
    ) is True


def test_resume_first_then_missing_jd():
    resume = create_resume_document(
        file_name="resume.pdf",
        file_bytes=b"resume content",
    )

    input_order = resolve_input_order(resume=resume)

    workflow_state = resolve_workflow_state(resume=resume)

    assert input_order == InputOrder.RESUME_FIRST
    assert workflow_state == WorkflowState.WAITING_FOR_JD

    result = handle_missing_jd(
        resume=resume,
        decision=MissingJDDecision.YES,
    )

    assert result.continue_without_jd is True
    assert result.resume_based_recommendations is True
    assert result.jd_based_recommendations is False


def test_jd_first_then_wait_for_resume():
    job_description = create_job_description(
        text="Data Scientist with Python and SQL.",
        title="Data Scientist",
    )

    input_order = resolve_input_order(
        job_description=job_description,
    )

    workflow_state = resolve_workflow_state(
        job_description=job_description,
    )

    assert input_order == InputOrder.JD_FIRST
    assert workflow_state == WorkflowState.WAITING_FOR_RESUME


def test_both_inputs_make_workflow_ready():
    resume = create_resume_document(
        file_name="resume.pdf",
        file_bytes=b"resume content",
    )

    job_description = create_job_description(
        text="Data Scientist with Python and SQL.",
        title="Data Scientist",
    )

    assert resolve_input_order(
        resume=resume,
        job_description=job_description,
    ) == InputOrder.BOTH

    assert is_workflow_ready(
        resume=resume,
        job_description=job_description,
    ) is True


def test_missing_jd_no_keeps_workflow_waiting():
    resume = create_resume_document(
        file_name="resume.pdf",
        file_bytes=b"resume content",
    )

    result = handle_missing_jd(
        resume=resume,
        decision=MissingJDDecision.NO,
    )

    assert result.continue_without_jd is False
    assert result.resume_based_recommendations is False
    assert result.jd_based_recommendations is False
    