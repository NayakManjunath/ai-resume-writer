from ai_resume_writer.alignment.matcher import align_resume_with_job_description
from ai_resume_writer.contracts.models import (
    CandidateProfile,
    JobDescription,
    TargetRole,
)


def test_matches_required_skills_case_insensitively():
    candidate = CandidateProfile(
        skills=["Python", "SQL"],
    )
    job_description = JobDescription(
        raw_text="Data Scientist",
        title="Data Scientist",
        required_skills=["python", "SQL", "Docker"],
    )
    target_role = TargetRole(
        designation="Data Scientist",
        source="jd",
    )

    result = align_resume_with_job_description(
        candidate_profile=candidate,
        job_description=job_description,
        target_role=target_role,
    )

    assert result.matched_required_skills == ["Python", "SQL"]
    assert result.missing_required_skills == ["Docker"]


def test_matches_preferred_skills():
    candidate = CandidateProfile(
        skills=["Python", "Pandas"],
    )
    job_description = JobDescription(
        raw_text="Data Scientist",
        title="Data Scientist",
        preferred_skills=["Pandas", "Docker"],
    )
    target_role = TargetRole(
        designation="Data Scientist",
        source="jd",
    )

    result = align_resume_with_job_description(
        candidate_profile=candidate,
        job_description=job_description,
        target_role=target_role,
    )

    assert result.matched_preferred_skills == ["Pandas"]
    assert result.missing_preferred_skills == ["Docker"]


def test_normalizes_skill_whitespace_and_case():
    candidate = CandidateProfile(
        skills=[" Python ", "sql"],
    )
    job_description = JobDescription(
        raw_text="Data Scientist",
        title="Data Scientist",
        required_skills=["PYTHON", " SQL "],
    )
    target_role = TargetRole(
        designation="Data Scientist",
        source="jd",
    )

    result = align_resume_with_job_description(
        candidate_profile=candidate,
        job_description=job_description,
        target_role=target_role,
    )

    assert result.matched_required_skills == [" Python ", "sql"]
    assert result.missing_required_skills == []


def test_reports_resume_only_skills():
    candidate = CandidateProfile(
        skills=["Python", "SQL", "Pandas"],
    )
    job_description = JobDescription(
        raw_text="Data Scientist",
        title="Data Scientist",
        required_skills=["Python"],
        preferred_skills=["SQL"],
    )
    target_role = TargetRole(
        designation="Data Scientist",
        source="jd",
    )

    result = align_resume_with_job_description(
        candidate_profile=candidate,
        job_description=job_description,
        target_role=target_role,
    )

    assert result.resume_only_skills == ["Pandas"]


def test_does_not_duplicate_matching_skills():
    candidate = CandidateProfile(
        skills=["Python", "python", "SQL"],
    )
    job_description = JobDescription(
        raw_text="Data Scientist",
        title="Data Scientist",
        required_skills=["Python", "python", "SQL"],
    )
    target_role = TargetRole(
        designation="Data Scientist",
        source="jd",
    )

    result = align_resume_with_job_description(
        candidate_profile=candidate,
        job_description=job_description,
        target_role=target_role,
    )

    assert result.matched_required_skills == ["Python", "SQL"]


def test_empty_skill_lists_produce_no_matches():
    candidate = CandidateProfile()
    job_description = JobDescription(
        raw_text="Data Scientist",
        title="Data Scientist",
    )
    target_role = TargetRole(
        designation="Data Scientist",
        source="jd",
    )

    result = align_resume_with_job_description(
        candidate_profile=candidate,
        job_description=job_description,
        target_role=target_role,
    )

    assert result.matched_required_skills == []
    assert result.missing_required_skills == []
    assert result.matched_preferred_skills == []
    assert result.missing_preferred_skills == []
    assert result.resume_only_skills == []


def test_extracts_and_compares_experience_requirement():
    candidate = CandidateProfile(
        experience_years=4.0,
    )
    job_description = JobDescription(
        raw_text="Data Scientist\n3+ years of experience required.",
        title="Data Scientist",
    )
    target_role = TargetRole(
        designation="Data Scientist",
        source="jd",
    )

    result = align_resume_with_job_description(
        candidate_profile=candidate,
        job_description=job_description,
        target_role=target_role,
    )

    assert result.required_experience_years == 3.0
    assert result.candidate_experience_years == 4.0
    assert result.meets_experience_requirement is True


def test_missing_experience_requirement_remains_none():
    candidate = CandidateProfile(
        experience_years=4.0,
    )
    job_description = JobDescription(
        raw_text="Data Scientist\nPython and SQL required.",
        title="Data Scientist",
        required_skills=["Python", "SQL"],
    )
    target_role = TargetRole(
        designation="Data Scientist",
        source="jd",
    )

    result = align_resume_with_job_description(
        candidate_profile=candidate,
        job_description=job_description,
        target_role=target_role,
    )

    assert result.required_experience_years is None
    assert result.candidate_experience_years == 4.0
    assert result.meets_experience_requirement is None


def test_preserves_role_evidence_without_semantic_guessing():
    candidate = CandidateProfile(
        experience=["Machine Learning Engineer - ABC"],
    )
    job_description = JobDescription(
        raw_text="Data Scientist",
        title="Data Scientist",
    )
    target_role = TargetRole(
        designation="Data Scientist",
        source="jd",
    )

    result = align_resume_with_job_description(
        candidate_profile=candidate,
        job_description=job_description,
        target_role=target_role,
    )

    assert result.target_role == target_role
    assert result.job_title == "Data Scientist"
    assert result.candidate_role_evidence == "Machine Learning Engineer - ABC"


def test_alignment_does_not_fabricate_missing_information():
    candidate = CandidateProfile(
        skills=["Python"],
        projects=[],
        experience=[],
    )
    job_description = JobDescription(
        raw_text="Data Scientist",
        title="Data Scientist",
        required_skills=["Python", "Docker"],
    )
    target_role = TargetRole(
        designation="Data Scientist",
        source="jd",
    )

    result = align_resume_with_job_description(
        candidate_profile=candidate,
        job_description=job_description,
        target_role=target_role,
    )

    assert result.matched_required_skills == ["Python"]
    assert result.missing_required_skills == ["Docker"]
    assert result.candidate_projects == []
    assert result.candidate_experience == []
