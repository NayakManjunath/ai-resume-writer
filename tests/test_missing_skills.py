from ai_resume_writer.contracts.models import (
    CandidateProfile,
    InformationStatus,
    JobDescription,
)
from ai_resume_writer.gap_analysis.skills import identify_missing_skills


def test_identifies_missing_required_skill():
    candidate = CandidateProfile(
        skills=["Python", "SQL"],
    )
    job_description = JobDescription(
        raw_text="Data Scientist",
        title="Data Scientist",
        required_skills=["Python", "SQL", "Docker"],
    )

    result = identify_missing_skills(
        candidate_profile=candidate,
        job_description=job_description,
    )

    assert len(result) == 1
    assert result[0].category == "required_skill"
    assert result[0].item == "Docker"
    assert result[0].status == InformationStatus.DETECTED


def test_identifies_missing_preferred_skill():
    candidate = CandidateProfile(
        skills=["Python", "SQL"],
    )
    job_description = JobDescription(
        raw_text="Data Scientist",
        title="Data Scientist",
        preferred_skills=["Pandas", "Docker"],
    )

    result = identify_missing_skills(
        candidate_profile=candidate,
        job_description=job_description,
    )

    assert [item.item for item in result] == ["Pandas", "Docker"]
    assert all(
        item.category == "preferred_skill"
        for item in result
    )


def test_separates_required_and_preferred_missing_skills():
    candidate = CandidateProfile(
        skills=["Python"],
    )
    job_description = JobDescription(
        raw_text="Data Scientist",
        title="Data Scientist",
        required_skills=["Python", "SQL"],
        preferred_skills=["Docker"],
    )

    result = identify_missing_skills(
        candidate_profile=candidate,
        job_description=job_description,
    )

    assert [(item.category, item.item) for item in result] == [
        ("required_skill", "SQL"),
        ("preferred_skill", "Docker"),
    ]


def test_skill_matching_is_case_insensitive():
    candidate = CandidateProfile(
        skills=["python", " SQL "],
    )
    job_description = JobDescription(
        raw_text="Data Scientist",
        title="Data Scientist",
        required_skills=["Python", "SQL"],
    )

    result = identify_missing_skills(
        candidate_profile=candidate,
        job_description=job_description,
    )

    assert result == []


def test_duplicate_jd_skills_create_only_one_gap():
    candidate = CandidateProfile(
        skills=["Python"],
    )
    job_description = JobDescription(
        raw_text="Data Scientist",
        title="Data Scientist",
        required_skills=["Docker", "docker", " Docker "],
    )

    result = identify_missing_skills(
        candidate_profile=candidate,
        job_description=job_description,
    )

    assert len(result) == 1
    assert result[0].item == "Docker"


def test_no_missing_skills_returns_empty_list():
    candidate = CandidateProfile(
        skills=["Python", "SQL", "Docker"],
    )
    job_description = JobDescription(
        raw_text="Data Scientist",
        title="Data Scientist",
        required_skills=["Python", "SQL"],
        preferred_skills=["Docker"],
    )

    result = identify_missing_skills(
        candidate_profile=candidate,
        job_description=job_description,
    )

    assert result == []


def test_empty_job_description_skill_lists_return_empty_list():
    candidate = CandidateProfile(
        skills=["Python", "SQL"],
    )
    job_description = JobDescription(
        raw_text="Data Scientist",
        title="Data Scientist",
    )

    result = identify_missing_skills(
        candidate_profile=candidate,
        job_description=job_description,
    )

    assert result == []


def test_gap_reason_is_a_question_about_experience():
    candidate = CandidateProfile(
        skills=["Python"],
    )
    job_description = JobDescription(
        raw_text="Data Scientist",
        title="Data Scientist",
        required_skills=["Docker"],
    )

    result = identify_missing_skills(
        candidate_profile=candidate,
        job_description=job_description,
    )

    assert result[0].reason == (
        "Docker appears relevant to the target role but was not found "
        "in your resume. Have you worked with Docker?"
    )


def test_missing_skill_does_not_claim_candidate_lacks_skill():
    candidate = CandidateProfile(
        skills=["Python"],
    )
    job_description = JobDescription(
        raw_text="Data Scientist",
        title="Data Scientist",
        required_skills=["Docker"],
    )

    result = identify_missing_skills(
        candidate_profile=candidate,
        job_description=job_description,
    )

    assert "do not know" not in result[0].reason.lower()
    assert "lack" not in result[0].reason.lower()
    assert "do not have" not in result[0].reason.lower()


def test_gap_items_are_detected_and_not_user_confirmed():
    candidate = CandidateProfile(
        skills=["Python"],
    )
    job_description = JobDescription(
        raw_text="Data Scientist",
        title="Data Scientist",
        required_skills=["Docker"],
    )

    result = identify_missing_skills(
        candidate_profile=candidate,
        job_description=job_description,
    )

    assert all(
        item.status == InformationStatus.DETECTED
        for item in result
    )
