
from pathlib import Path

import pytest

from ai_resume_writer.contracts.models import (
    JobDescription,
    ResumeDocument,
)
from ai_resume_writer.jd.input import JobDescriptionInputError
from ai_resume_writer.resume.extractor import ResumeExtractionError
from ai_resume_writer.resume.uploader import ResumeUploadError
from ai_resume_writer.ui.input_page import (
    load_job_description,
    load_resume_upload,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures"


def test_load_resume_upload_from_pdf():
    resume_path = FIXTURE_DIR / "sample_resume.pdf"

    resume = load_resume_upload(
        file_name=resume_path.name,
        file_bytes=resume_path.read_bytes(),
    )

    assert isinstance(resume, ResumeDocument)
    assert resume.file_type == "pdf"
    assert resume.raw_text.strip()


def test_load_resume_upload_from_docx():
    resume_path = FIXTURE_DIR / "sample_resume.docx"

    resume = load_resume_upload(
        file_name=resume_path.name,
        file_bytes=resume_path.read_bytes(),
    )

    assert isinstance(resume, ResumeDocument)
    assert resume.file_type == "docx"
    assert resume.raw_text.strip()


def test_load_resume_upload_rejects_unsupported_extension():
    with pytest.raises(ResumeUploadError):
        load_resume_upload(
            file_name="resume.txt",
            file_bytes=b"Some resume text",
        )


def test_load_resume_upload_rejects_empty_file():
    with pytest.raises(ResumeUploadError):
        load_resume_upload(
            file_name="resume.pdf",
            file_bytes=b"",
        )


def test_load_resume_upload_rejects_unreadable_pdf():
    with pytest.raises(ResumeExtractionError):
        load_resume_upload(
            file_name="resume.pdf",
            file_bytes=b"not a valid PDF document",
        )


def test_load_job_description():
    result = load_job_description(
        "Data Scientist\nRequired skills: Python, SQL"
    )

    assert isinstance(result, JobDescription)
    assert "Data Scientist" in result.raw_text
    assert "Python" in result.raw_text


def test_load_job_description_rejects_blank_text():
    with pytest.raises(JobDescriptionInputError):
        load_job_description("   \n  ")
