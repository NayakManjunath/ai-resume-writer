import pytest

from ai_resume_writer.contracts.models import ResumeDocument
from ai_resume_writer.resume.parser import (
    ResumeInformationParsingError,
    parse_resume_information,
)


def test_parse_resume_information():
    resume = ResumeDocument(
        file_name="resume.pdf",
        file_type="pdf",
        raw_text="""
        John Doe

        Professional Summary
        Data Scientist with experience in machine learning.

        Skills
        Python
        SQL
        Pandas

        Experience
        Data Scientist | ABC Technologies | 2024-Present
        Built machine learning models.

        Projects
        Sales Forecasting System
        Customer Churn Prediction

        Education
        B.Tech in Computer Science

        Certifications
        AWS Certified Cloud Practitioner
        """,
    )

    profile = parse_resume_information(resume)

    assert profile.name == "John Doe"

    assert (
        profile.professional_summary
        == "Data Scientist with experience in machine learning."
    )

    assert profile.skills == [
        "Python",
        "SQL",
        "Pandas",
    ]

    assert profile.experience == [
        "Data Scientist | ABC Technologies | 2024-Present",
        "Built machine learning models.",
    ]

    assert profile.projects == [
        "Sales Forecasting System",
        "Customer Churn Prediction",
    ]

    assert profile.education == [
        "B.Tech in Computer Science",
    ]

    assert profile.certifications == [
        "AWS Certified Cloud Practitioner",
    ]

    # Experience calculation belongs to 3.4.
    assert profile.experience_years is None


def test_parse_resume_without_optional_sections():
    resume = ResumeDocument(
        file_name="resume.pdf",
        file_type="pdf",
        raw_text="""
        Jane Doe

        Skills
        Python
        SQL
        """,
    )

    profile = parse_resume_information(resume)

    assert profile.name == "Jane Doe"
    assert profile.skills == ["Python", "SQL"]
    assert profile.professional_summary is None
    assert profile.projects == []
    assert profile.experience == []
    assert profile.education == []
    assert profile.certifications == []
    assert profile.experience_years is None


def test_parse_resume_rejects_empty_text():
    resume = ResumeDocument(
        file_name="resume.pdf",
        file_type="pdf",
        raw_text="",
    )

    with pytest.raises(ResumeInformationParsingError):
        parse_resume_information(resume)