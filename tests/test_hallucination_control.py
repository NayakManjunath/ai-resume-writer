from ai_resume_writer.contracts.models import CandidateProfile
from ai_resume_writer.rewrite.hallucination import validate_generated_resume


def test_supported_candidate_skill_is_preserved():
    profile = CandidateProfile(
        skills=["Python", "FastAPI"],
    )

    generated = {
        "skills": ["Python", "FastAPI"],
    }

    result = validate_generated_resume(profile, generated)

    assert result["skills"] == ["Python", "FastAPI"]


def test_unsupported_skill_is_removed():
    profile = CandidateProfile(
        skills=["Python", "FastAPI"],
    )

    generated = {
        "skills": ["Python", "FastAPI", "Kubernetes"],
    }

    result = validate_generated_resume(profile, generated)

    assert result["skills"] == ["Python", "FastAPI"]


def test_jd_only_skill_cannot_become_candidate_skill():
    profile = CandidateProfile(
        skills=["Python", "FastAPI"],
    )

    generated = {
        "skills": ["Python", "FastAPI", "Kubernetes"],
    }

    result = validate_generated_resume(profile, generated)

    assert "Kubernetes" not in result["skills"]


def test_unsupported_project_is_rejected_when_source_is_empty():
    profile = CandidateProfile(
        projects=[],
    )

    generated = {
        "projects": ["Fraud Detection System"],
    }

    result = validate_generated_resume(profile, generated)

    assert result["projects"] == []


def test_unsupported_metric_is_rejected():
    profile = CandidateProfile(
        experience=[
            "Built machine learning models using Python.",
        ],
    )

    generated = {
        "experience": [
            "Built machine learning models using Python with 95% accuracy."
        ],
    }

    result = validate_generated_resume(profile, generated)

    assert result["experience"] == []


def test_existing_metric_is_preserved():
    profile = CandidateProfile(
        experience=[
            "Improved processing speed by 30%.",
        ],
    )

    generated = {
        "experience": [
            "Improved processing speed by 30%."
        ],
    }

    result = validate_generated_resume(profile, generated)

    assert result["experience"] == [
        "Improved processing speed by 30%."
    ]


def test_unsupported_section_is_not_returned():
    profile = CandidateProfile(
        skills=["Python"],
    )

    generated = {
        "skills": ["Python"],
        "awards": ["Best AI Engineer Award"],
    }

    result = validate_generated_resume(profile, generated)

    assert "awards" not in result
    assert result["skills"] == ["Python"]


def test_empty_candidate_section_cannot_receive_generated_content():
    profile = CandidateProfile(
        certifications=[],
    )

    generated = {
        "certifications": [
            "Google Professional Data Engineer",
        ],
    }

    result = validate_generated_resume(profile, generated)

    assert result["certifications"] == []


def test_legitimate_rewording_is_preserved():
    profile = CandidateProfile(
        experience=[
            "Worked on machine learning models using Python.",
        ],
    )

    generated = {
        "experience": [
            "Developed machine learning models using Python.",
        ],
    }

    result = validate_generated_resume(profile, generated)

    assert result["experience"] == [
        "Developed machine learning models using Python.",
    ]


def test_original_profile_is_not_modified():
    profile = CandidateProfile(
        skills=["Python"],
        projects=["Resume Parser"],
        experience=[
            "Worked with Python.",
        ],
    )

    original = profile.model_copy(deep=True)

    generated = {
        "skills": ["Python", "Kubernetes"],
        "projects": ["Resume Parser", "Fraud Detection"],
        "experience": [
            "Worked with Python with 95% accuracy.",
        ],
    }

    validate_generated_resume(profile, generated)

    assert profile == original


def test_unsupported_certification_is_rejected_when_source_is_empty():
    profile = CandidateProfile(
        certifications=[],
    )

    generated = {
        "certifications": [
            "AWS Certified Machine Learning",
        ],
    }

    result = validate_generated_resume(profile, generated)

    assert result["certifications"] == []


def test_unsupported_education_is_rejected_when_source_is_empty():
    profile = CandidateProfile(
        education=[],
    )

    generated = {
        "education": [
            "M.Tech in Artificial Intelligence",
        ],
    }

    result = validate_generated_resume(profile, generated)

    assert result["education"] == []