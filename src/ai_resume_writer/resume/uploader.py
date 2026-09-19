from pathlib import Path

from ai_resume_writer.contracts.models import ResumeDocument


SUPPORTED_RESUME_TYPES = {
    ".pdf": "pdf",
    ".docx": "docx",
}


class ResumeUploadError(ValueError):
    """Raised when an uploaded resume fails validation."""


def validate_resume_file(
    file_name: str,
    file_bytes: bytes,
) -> str:
    """
    Validate an uploaded resume and return its normalized file type.
    """

    if not file_name or not file_name.strip():
        raise ResumeUploadError(
            "Resume file name cannot be empty."
        )

    if not file_bytes:
        raise ResumeUploadError(
            "Resume file cannot be empty."
        )

    extension = Path(file_name).suffix.lower()

    if extension not in SUPPORTED_RESUME_TYPES:
        supported = ", ".join(
            SUPPORTED_RESUME_TYPES.keys()
        )
        raise ResumeUploadError(
            f"Unsupported resume format. "
            f"Supported formats: {supported}"
        )

    return SUPPORTED_RESUME_TYPES[extension]


def create_resume_document(
    file_name: str,
    file_bytes: bytes,
) -> ResumeDocument:
    """
    Validate an uploaded resume and create its data contract.

    Text extraction is intentionally not performed here.
    """

    file_type = validate_resume_file(
        file_name=file_name,
        file_bytes=file_bytes,
    )

    return ResumeDocument(
        file_name=file_name,
        file_type=file_type,
        raw_text="",
    )