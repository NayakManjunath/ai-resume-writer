import pytest

from ai_resume_writer.contracts.models import JobDescription
from ai_resume_writer.jd.parser import (
    JobDescriptionParsingError,
    parse_job_description,
)


def test_parse_job_description():
    jd = JobDescription(
        raw_text="""
        Data Scientist

        Required Skills
        Python
        SQL
        Machine Learning

        Preferred Skills
        AWS
        Docker
        """,
    )

    parsed = parse_job_description(jd)

    assert parsed.title == "Data Scientist"

    assert parsed.required_skills == [
        "Python",
        "SQL",
        "Machine Learning",
    ]

    assert parsed.preferred_skills == [
        "AWS",
        "Docker",
    ]


def test_existing_title_takes_precedence():
    jd = JobDescription(
        raw_text="""
        Senior Data Scientist

        Required Skills
        Python
        SQL
        """,
        title="Data Scientist",
    )

    parsed = parse_job_description(jd)

    assert parsed.title == "Data Scientist"
    assert parsed.required_skills == ["Python", "SQL"]


def test_comma_separated_skills():
    jd = JobDescription(
        raw_text="""
        Data Scientist

        Required Skills
        Python, SQL, Pandas, NumPy
        """,
    )

    parsed = parse_job_description(jd)

    assert parsed.required_skills == [
        "Python",
        "SQL",
        "Pandas",
        "NumPy",
    ]


def test_missing_optional_sections():
    jd = JobDescription(
        raw_text="""
        Data Scientist

        Required Skills
        Python
        SQL
        """,
    )

    parsed = parse_job_description(jd)

    assert parsed.required_skills == [
        "Python",
        "SQL",
    ]

    assert parsed.preferred_skills == []


def test_empty_job_description_is_rejected():
    jd = JobDescription(
        raw_text="",
    )

    with pytest.raises(JobDescriptionParsingError):
        parse_job_description(jd)
