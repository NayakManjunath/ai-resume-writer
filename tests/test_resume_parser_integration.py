from pathlib import Path

from ai_resume_writer.resume.extractor import extract_resume
from ai_resume_writer.resume.parser import parse_resume_information


FIXTURE_DIR = Path(__file__).parent / "fixtures"


def test_parse_extracted_pdf_resume():
    resume_path = FIXTURE_DIR / "sample_resume.pdf"

    resume = extract_resume(
        file_name=resume_path.name,
        file_bytes=resume_path.read_bytes(),
    )

    profile = parse_resume_information(resume)

    assert profile.name == "Test Candidate"
    assert profile.skills == ["Python, SQL"]
    assert profile.experience == ["Data Scientist - Test Company"]
    assert profile.projects == []
    assert profile.experience_years is None


def test_parse_extracted_docx_resume():
    resume_path = FIXTURE_DIR / "sample_resume.docx"

    resume = extract_resume(
        file_name=resume_path.name,
        file_bytes=resume_path.read_bytes(),
    )

    profile = parse_resume_information(resume)

    assert profile.name == "Test Candidate"
    assert profile.skills == ["Python, SQL, Pandas"]
    assert profile.experience == ["Data Scientist - Test Company"]
    assert profile.projects == []
    assert profile.experience_years is None
