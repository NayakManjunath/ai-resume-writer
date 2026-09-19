from enum import Enum

from ai_resume_writer.contracts.models import (
    JobDescription,
    ResumeDocument,
)


class InputOrder(str, Enum):
    RESUME_FIRST = "resume_first"
    JD_FIRST = "jd_first"
    BOTH = "both"


class WorkflowState(str, Enum):
    WAITING_FOR_RESUME = "waiting_for_resume"
    WAITING_FOR_JD = "waiting_for_jd"
    READY_FOR_ANALYSIS = "ready_for_analysis"


class InputWorkflowError(ValueError):
    """Raised when the input workflow receives invalid state."""


def resolve_input_order(
    resume: ResumeDocument | None = None,
    job_description: JobDescription | None = None,
) -> InputOrder:
    """Determine which inputs are currently available."""

    if resume is not None and job_description is not None:
        return InputOrder.BOTH

    if resume is not None:
        return InputOrder.RESUME_FIRST

    if job_description is not None:
        return InputOrder.JD_FIRST

    raise InputWorkflowError(
        "At least a resume or Job Description must be provided."
    )


def resolve_workflow_state(
    resume: ResumeDocument | None = None,
    job_description: JobDescription | None = None,
) -> WorkflowState:
    """Determine what input is required next."""

    if resume is not None and job_description is not None:
        return WorkflowState.READY_FOR_ANALYSIS

    if resume is not None:
        return WorkflowState.WAITING_FOR_JD

    if job_description is not None:
        return WorkflowState.WAITING_FOR_RESUME

    return WorkflowState.WAITING_FOR_RESUME


def is_workflow_ready(
    resume: ResumeDocument | None = None,
    job_description: JobDescription | None = None,
) -> bool:
    """Return True only when both required inputs are available."""

    return resume is not None and job_description is not None