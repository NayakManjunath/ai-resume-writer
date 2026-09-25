from ai_resume_writer.jd.input import create_job_description
from ai_resume_writer.jd.parser import parse_job_description


def test_job_description_input_to_structured_understanding():
    job_description = create_job_description(
        text="""
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

    parsed = parse_job_description(job_description)

    assert parsed.raw_text == job_description.raw_text
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


def test_job_description_input_normalization_reaches_parser():
    job_description = create_job_description(
        text="""

        Senior Data Scientist

        Required Skills:
        Python, SQL, Pandas

        Preferred Skills:
        AWS, Docker

        """,
    )

    parsed = parse_job_description(job_description)

    assert parsed.title == "Senior Data Scientist"

    assert parsed.required_skills == [
        "Python",
        "SQL",
        "Pandas",
    ]

    assert parsed.preferred_skills == [
        "AWS",
        "Docker",
    ]
