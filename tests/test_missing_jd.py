import pytest

from ai_resume_writer.contracts.models import ResumeDocument
from ai_resume_writer.jd.missing import (
    MISSING_JD_QUESTION,
    MissingJDDecision,
    MissingJDHandlingError,
    get_missing_jd_question,
    handle_missing_jd,
)


@pytest.fixture
def sample_resume() -> ResumeDocument:
    return ResumeDocument(
        file_name="resume.pdf",
        file_type="pdf",
        raw_text="John Doe\nData Scientist\nPython SQL Machine Learning",
        sections=["Skills"],
    )


def test_missing_jd_question_is_exact():
    assert (
        get_missing_jd_question()
        == "Would you like to continue without Job Description?"
    )


def test_missing_jd_yes_allows_resume_based_analysis(sample_resume):
    result = handle_missing_jd(
        resume=sample_resume,
        decision=MissingJDDecision.YES,
    )

    assert result.continue_without_jd is True
    assert result.resume_based_recommendations is True
    assert result.jd_based_recommendations is False


def test_missing_jd_no_waits_for_jd(sample_resume):
    result = handle_missing_jd(
        resume=sample_resume,
        decision=MissingJDDecision.NO,
    )

    assert result.continue_without_jd is False
    assert result.resume_based_recommendations is False
    assert result.jd_based_recommendations is False


def test_missing_jd_requires_resume():
    with pytest.raises(MissingJDHandlingError):
        handle_missing_jd(
            resume=None,
            decision=MissingJDDecision.YES,
        )
        