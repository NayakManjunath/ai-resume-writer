from enum import Enum

from pydantic import BaseModel

from ai_resume_writer.contracts.models import ResumeDocument


MISSING_JD_QUESTION = "Would you like to continue without Job Description?"


class MissingJDDecision(str, Enum):
    YES = "yes"
    NO = "no"


class MissingJDHandling(BaseModel):
    question: str
    decision: MissingJDDecision
    continue_without_jd: bool
    resume_based_recommendations: bool
    jd_based_recommendations: bool


class MissingJDHandlingError(ValueError):
    """Raised when missing JD handling receives invalid input."""


def get_missing_jd_question() -> str:
    return MISSING_JD_QUESTION


def handle_missing_jd(
    resume: ResumeDocument | None,
    decision: MissingJDDecision,
) -> MissingJDHandling:
    if resume is None:
        raise MissingJDHandlingError(
            "A resume is required before handling a missing Job Description."
        )

    if decision == MissingJDDecision.YES:
        return MissingJDHandling(
            question=MISSING_JD_QUESTION,
            decision=decision,
            continue_without_jd=True,
            resume_based_recommendations=True,
            jd_based_recommendations=False,
        )

    return MissingJDHandling(
        question=MISSING_JD_QUESTION,
        decision=decision,
        continue_without_jd=False,
        resume_based_recommendations=False,
        jd_based_recommendations=False,
    )
