from ai_resume_writer.contracts.models import (
    CandidateProfile,
    InformationStatus,
    JobDescription,
)
from ai_resume_writer.gap_analysis.projects_sections import (
    identify_missing_projects_and_sections,
)


def test_identifies_missing_projects_when_jd_explicitly_requires_projects():
    candidate = CandidateProfile(
        skills=["Python", "SQL"],
        projects=[],
    )
    job_description = JobDescription(
        raw_text=(
            "Data Scientist\n"
            "Hands-on projects involving machine learning are required."
        ),
        title="Data Scientist",
        required_skills=["Python", "SQL"],
    )

    result = identify_missing_projects_and_sections(
        candidate_profile=candidate,
        job_description=job_description,
    )

    assert len(result) == 1
    assert result[0].category == "missing_project"
    assert result[0].item == "Projects"
    assert result[0].status == InformationStatus.DETECTED


def test_existing_projects_produce_no_missing_project_gap():
    candidate = CandidateProfile(
        skills=["Python"],
        projects=["Customer churn prediction"],
    )
    job_description = JobDescription(
        raw_text=(
            "Data Scientist\n"
            "Hands-on projects involving machine learning are required."
        ),
        title="Data Scientist",
        required_skills=["Python"],
    )

    result = identify_missing_projects_and_sections(
        candidate_profile=candidate,
        job_description=job_description,
    )

    assert result == []


def test_detects_project_evidence_case_insensitively():
    candidate = CandidateProfile(
        projects=[],
    )
    job_description = JobDescription(
        raw_text=(
            "Data Scientist\n"
            "Candidates should have PORTFOLIO PROJECTS demonstrating "
            "practical machine learning experience."
        ),
        title="Data Scientist",
    )

    result = identify_missing_projects_and_sections(
        candidate_profile=candidate,
        job_description=job_description,
    )

    assert len(result) == 1
    assert result[0].item == "Projects"


def test_missing_project_gap_uses_review_question():
    candidate = CandidateProfile(
        projects=[],
    )
    job_description = JobDescription(
        raw_text=(
            "Data Scientist\n"
            "Hands-on projects involving machine learning are required."
        ),
        title="Data Scientist",
    )

    result = identify_missing_projects_and_sections(
        candidate_profile=candidate,
        job_description=job_description,
    )

    assert result[0].reason == (
        "Project experience appears relevant to the target role but "
        "was not found in your resume. Do you have a relevant project "
        "you would like to include?"
    )


def test_missing_project_gap_does_not_invent_a_project():
    candidate = CandidateProfile(
        projects=[],
    )
    job_description = JobDescription(
        raw_text=(
            "Data Scientist\n"
            "Hands-on projects involving machine learning are required."
        ),
        title="Data Scientist",
    )

    result = identify_missing_projects_and_sections(
        candidate_profile=candidate,
        job_description=job_description,
    )

    assert result[0].item == "Projects"
    assert "churn" not in result[0].reason.lower()
    assert "prediction" not in result[0].reason.lower()


def test_skills_alone_do_not_create_missing_project_gap():
    candidate = CandidateProfile(
        skills=["Python"],
        projects=[],
    )
    job_description = JobDescription(
        raw_text="Data Scientist\nStrong Python and SQL skills required.",
        title="Data Scientist",
        required_skills=["Python", "SQL"],
    )

    result = identify_missing_projects_and_sections(
        candidate_profile=candidate,
        job_description=job_description,
    )

    assert result == []


def test_missing_relevant_section_is_detected_from_explicit_jd_evidence():
    candidate = CandidateProfile(
        professional_summary=None,
        projects=["Forecasting project"],
    )
    job_description = JobDescription(
        raw_text=(
            "Data Scientist\n"
            "Candidates should provide a professional summary "
            "highlighting relevant experience."
        ),
        title="Data Scientist",
    )

    result = identify_missing_projects_and_sections(
        candidate_profile=candidate,
        job_description=job_description,
    )

    assert len(result) == 1
    assert result[0].category == "missing_section"
    assert result[0].item == "Professional Summary"
    assert result[0].status == InformationStatus.DETECTED


def test_existing_relevant_section_produces_no_section_gap():
    candidate = CandidateProfile(
        professional_summary="Data Scientist with Python experience.",
        projects=[],
    )
    job_description = JobDescription(
        raw_text=(
            "Data Scientist\n"
            "Candidates should provide a professional summary "
            "highlighting relevant experience."
        ),
        title="Data Scientist",
    )

    result = identify_missing_projects_and_sections(
        candidate_profile=candidate,
        job_description=job_description,
    )

    assert result == []


def test_empty_jd_evidence_produces_no_project_or_section_gap():
    candidate = CandidateProfile(
        professional_summary=None,
        projects=[],
    )
    job_description = JobDescription(
        raw_text="Data Scientist\nPython and SQL required.",
        title="Data Scientist",
    )

    result = identify_missing_projects_and_sections(
        candidate_profile=candidate,
        job_description=job_description,
    )

    assert result == []


def test_duplicate_project_evidence_creates_one_gap():
    candidate = CandidateProfile(
        projects=[],
    )
    job_description = JobDescription(
        raw_text=(
            "Data Scientist\n"
            "Portfolio projects are required.\n"
            "Candidates should also provide project experience."
        ),
        title="Data Scientist",
    )

    result = identify_missing_projects_and_sections(
        candidate_profile=candidate,
        job_description=job_description,
    )

    project_gaps = [
        item for item in result
        if item.category == "missing_project"
    ]

    assert len(project_gaps) == 1
    assert project_gaps[0].item == "Projects"
