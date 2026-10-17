
from pathlib import Path

from ai_resume_writer.jd.input import create_job_description
from ai_resume_writer.resume.extractor import extract_resume
from ai_resume_writer.resume.workflow import (
    InputOrder,
    WorkflowState,
    is_workflow_ready,
    resolve_input_order,
    resolve_workflow_state,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures"


def test_resume_first_then_job_description():
    resume_path = FIXTURE_DIR / "sample_resume.pdf"
    resume = extract_resume(
        file_name=resume_path.name,
        file_bytes=resume_path.read_bytes(),
    )

    assert resolve_input_order(resume=resume) == InputOrder.RESUME_FIRST
    assert (
        resolve_workflow_state(resume=resume)
        == WorkflowState.WAITING_FOR_JD
    )

    jd = create_job_description(
        text="Data Scientist. Required skills: Python and SQL."
    )

    assert is_workflow_ready(resume=resume, job_description=jd)
    assert (
        resolve_workflow_state(resume=resume, job_description=jd)
        == WorkflowState.READY_FOR_ANALYSIS
    )


def test_job_description_first_then_resume():
    jd = create_job_description(
        text="Data Scientist. Required skills: Python and SQL."
    )

    assert resolve_input_order(job_description=jd) == InputOrder.JD_FIRST
    assert (
        resolve_workflow_state(job_description=jd)
        == WorkflowState.WAITING_FOR_RESUME
    )

    resume_path = FIXTURE_DIR / "sample_resume.pdf"
    resume = extract_resume(
        file_name=resume_path.name,
        file_bytes=resume_path.read_bytes(),
    )

    assert is_workflow_ready(resume=resume, job_description=jd)
    assert (
        resolve_workflow_state(resume=resume, job_description=jd)
        == WorkflowState.READY_FOR_ANALYSIS
    )


def test_both_inputs_together():
    resume_path = FIXTURE_DIR / "sample_resume.pdf"
    resume = extract_resume(
        file_name=resume_path.name,
        file_bytes=resume_path.read_bytes(),
    )
    jd = create_job_description(
        text="Data Scientist. Required skills: Python and SQL."
    )

    assert (
        resolve_input_order(resume=resume, job_description=jd)
        == InputOrder.BOTH
    )
    assert is_workflow_ready(resume=resume, job_description=jd)
