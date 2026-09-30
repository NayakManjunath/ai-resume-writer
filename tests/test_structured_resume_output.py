from unittest.mock import patch

import pytest

from ai_resume_writer.contracts.models import (
    CandidateProfile,
    JobDescription,
    ResumeFormatChoice,
    TargetRole,
)
from ai_resume_writer.rewrite.resume import rewrite_resume
from ai_resume_writer.rewrite.tailoring import tailor_resume
from ai_resume_writer.rewrite.hallucination import validate_generated_resume


@pytest.fixture
def candidate_profile():
    return CandidateProfile(
        name="Manjunath Naik",
        professional_summary="Data Scientist with experience building ML systems.",
        skills=[
            "Python",
            "SQL",
            "Machine Learning",
            "FastAPI",
        ],
        experience=[
            "Built machine learning services using Python and FastAPI.",
            "Improved document processing efficiency by 35%.",
        ],
        projects=[
            "Built a document intelligence system using NLP."
        ],
        education=[
            "Bachelor of Engineering"
        ],
        certifications=[
            "Data Science Certification"
        ],
    )


@pytest.fixture
def target_role():
    return TargetRole(
        designation="Data Scientist",
        source="job_description",
    )


@pytest.fixture
def job_description():
    return JobDescription(
        raw_text=(
            "Data Scientist role requiring Python, SQL, "
            "Machine Learning and FastAPI."
        ),
        title="Data Scientist",
        required_skills=[
            "Python",
            "SQL",
            "Machine Learning",
        ],
        preferred_skills=[
            "FastAPI",
        ],
    )


def test_structured_output_contains_allowed_sections(candidate_profile):
    generated_sections = {
        "professional_summary": [
            "Data Scientist with experience building ML systems."
        ],
        "skills": [
            "Python",
            "SQL",
            "Machine Learning",
            "FastAPI",
        ],
        "experience": [
            "Built machine learning services using Python and FastAPI."
        ],
        "projects": [
            "Built a document intelligence system using NLP."
        ],
        "education": [
            "Bachelor of Engineering"
        ],
        "certifications": [
            "Data Science Certification"
        ],
    }

    result = validate_generated_resume(
        candidate_profile=candidate_profile,
        generated_sections=generated_sections,
    )

    assert set(result).issubset(
        {
            "professional_summary",
            "skills",
            "experience",
            "projects",
            "education",
            "certifications",
        }
    )


def test_structured_output_preserves_supported_content(candidate_profile):
    generated_sections = {
        "skills": [
            "Python",
            "SQL",
            "Machine Learning",
        ],
        "experience": [
            "Built machine learning services using Python and FastAPI."
        ],
    }

    result = validate_generated_resume(
        candidate_profile=candidate_profile,
        generated_sections=generated_sections,
    )

    assert result["skills"] == [
        "Python",
        "SQL",
        "Machine Learning",
    ]

    assert result["experience"] == [
        "Built machine learning services using Python and FastAPI."
    ]


def test_structured_output_rejects_unsupported_section(candidate_profile):
    generated_sections = {
        "skills": ["Python"],
        "references": ["Available on request"],
    }

    result = validate_generated_resume(
        candidate_profile=candidate_profile,
        generated_sections=generated_sections,
    )

    assert "references" not in result


def test_structured_output_rejects_unsupported_skill(candidate_profile):
    generated_sections = {
        "skills": [
            "Python",
            "TensorFlow",
        ]
    }

    result = validate_generated_resume(
        candidate_profile=candidate_profile,
        generated_sections=generated_sections,
    )

    assert result["skills"] == ["Python"]
    assert "TensorFlow" not in result["skills"]


def test_structured_output_rejects_unsupported_metric(candidate_profile):
    generated_sections = {
        "experience": [
            "Improved document processing efficiency by 50%."
        ]
    }

    result = validate_generated_resume(
        candidate_profile=candidate_profile,
        generated_sections=generated_sections,
    )

    assert result["experience"] == []


def test_structured_output_preserves_existing_metric(candidate_profile):
    generated_sections = {
        "experience": [
            "Improved document processing efficiency by 35%."
        ]
    }

    result = validate_generated_resume(
        candidate_profile=candidate_profile,
        generated_sections=generated_sections,
    )

    assert result["experience"] == [
        "Improved document processing efficiency by 35%."
    ]


def test_empty_candidate_section_remains_empty(candidate_profile):
    profile_without_projects = candidate_profile.model_copy(
        update={"projects": []}
    )

    generated_sections = {
        "projects": [
            "Built an advanced computer vision system."
        ]
    }

    result = validate_generated_resume(
        candidate_profile=profile_without_projects,
        generated_sections=generated_sections,
    )

    assert result["projects"] == []


def test_legitimate_rewording_is_preserved(candidate_profile):
    generated_sections = {
        "experience": [
            "Developed machine learning services with Python and FastAPI."
        ]
    }

    result = validate_generated_resume(
        candidate_profile=candidate_profile,
        generated_sections=generated_sections,
    )

    assert result["experience"] == [
        "Developed machine learning services with Python and FastAPI."
    ]


def test_original_profile_is_not_modified(candidate_profile):
    original_profile = candidate_profile.model_copy(deep=True)

    generated_sections = {
        "skills": ["Python"],
        "experience": [
            "Developed machine learning services with Python and FastAPI."
        ],
    }

    validate_generated_resume(
        candidate_profile=candidate_profile,
        generated_sections=generated_sections,
    )

    assert candidate_profile == original_profile


@patch("ai_resume_writer.rewrite.resume._generate_rewrite")
def test_regular_rewrite_returns_structured_resume_improvement(
    mock_generate,
    candidate_profile,
    target_role,
):
    mock_generate.return_value = {
        "professional_summary": [
            "Data Scientist with experience building ML systems."
        ],
        "skills": [
            "Python",
            "SQL",
            "Machine Learning",
        ],
        "experience": [
            "Built machine learning services using Python and FastAPI."
        ],
    }

    result = rewrite_resume(
        candidate_profile=candidate_profile,
        target_role=target_role,
    )

    assert result.target_role == target_role
    assert result.format_choice == ResumeFormatChoice.KEEP_EXISTING
    assert result.original_profile == candidate_profile
    assert isinstance(result.improved_sections, dict)
    assert result.improved_sections["skills"] == [
        "Python",
        "SQL",
        "Machine Learning",
    ]


@patch("ai_resume_writer.rewrite.tailoring._generate_tailored_rewrite")
def test_jd_tailoring_returns_structured_resume_improvement(
    mock_generate,
    candidate_profile,
    target_role,
    job_description,
):
    mock_generate.return_value = {
        "professional_summary": [
            "Data Scientist with experience building ML systems."
        ],
        "skills": [
            "Python",
            "SQL",
            "Machine Learning",
            "FastAPI",
        ],
        "experience": [
            "Built machine learning services using Python and FastAPI."
        ],
    }

    result = tailor_resume(
        candidate_profile=candidate_profile,
        job_description=job_description,
        target_role=target_role,
    )

    assert result.target_role == target_role
    assert result.format_choice == ResumeFormatChoice.KEEP_EXISTING
    assert result.original_profile == candidate_profile
    assert isinstance(result.improved_sections, dict)
    assert result.improved_sections["skills"] == [
        "Python",
        "SQL",
        "Machine Learning",
        "FastAPI",
    ]