from ai_resume_writer.contracts.models import (
    CandidateProfile,
    JobDescription,
)
from ai_resume_writer.role.resolver import resolve_target_role


def test_user_designation_has_highest_priority() -> None:
    job_description = JobDescription(
        raw_text="Senior Data Scientist",
        title="Senior Data Scientist",
    )
    candidate_profile = CandidateProfile(
        experience=["Data Scientist - Example Company"],
    )

    result = resolve_target_role(
        user_designation="Machine Learning Engineer",
        job_description=job_description,
        candidate_profile=candidate_profile,
    )

    assert result is not None
    assert result.designation == "Machine Learning Engineer"
    assert result.source == "user"


def test_jd_title_is_used_when_user_designation_is_missing() -> None:
    job_description = JobDescription(
        raw_text="Senior Data Scientist",
        title="Senior Data Scientist",
    )
    candidate_profile = CandidateProfile(
        experience=["Data Scientist - Example Company"],
    )

    result = resolve_target_role(
        job_description=job_description,
        candidate_profile=candidate_profile,
    )

    assert result is not None
    assert result.designation == "Senior Data Scientist"
    assert result.source == "jd"


def test_resume_designation_is_used_when_user_and_jd_are_missing() -> None:
    candidate_profile = CandidateProfile(
        experience=["Data Scientist - Example Company"],
    )

    result = resolve_target_role(
        candidate_profile=candidate_profile,
    )

    assert result is not None
    assert result.designation == "Data Scientist - Example Company"
    assert result.source == "resume"


def test_jd_takes_precedence_when_jd_and_resume_disagree() -> None:
    job_description = JobDescription(
        raw_text="Machine Learning Engineer",
        title="Machine Learning Engineer",
    )
    candidate_profile = CandidateProfile(
        experience=["Data Scientist - Example Company"],
    )

    result = resolve_target_role(
        job_description=job_description,
        candidate_profile=candidate_profile,
    )

    assert result is not None
    assert result.designation == "Machine Learning Engineer"
    assert result.source == "jd"


def test_missing_designation_returns_none() -> None:
    result = resolve_target_role()

    assert result is None


def test_blank_user_designation_is_treated_as_missing() -> None:
    job_description = JobDescription(
        raw_text="Data Scientist",
        title="Data Scientist",
    )

    result = resolve_target_role(
        user_designation="   ",
        job_description=job_description,
    )

    assert result is not None
    assert result.designation == "Data Scientist"
    assert result.source == "jd"