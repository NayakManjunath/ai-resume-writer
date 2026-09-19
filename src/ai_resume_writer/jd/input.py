from ai_resume_writer.contracts.models import JobDescription


class JobDescriptionInputError(ValueError):
    """Raised when a job description fails validation."""


def _clean_text(text: str) -> str:
    """Normalize whitespace while preserving line structure."""

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    return "\n".join(lines)


def create_job_description(
    text: str,
    title: str | None = None,
) -> JobDescription:
    """
    Validate and create a JobDescription contract.

    JD interpretation and skill extraction are intentionally
    handled by later tracker stages.
    """

    if not text or not text.strip():
        raise JobDescriptionInputError(
            "Job Description cannot be empty."
        )

    cleaned_text = _clean_text(text)

    if not cleaned_text:
        raise JobDescriptionInputError(
            "Job Description must contain usable text."
        )

    cleaned_title = title.strip() if title else None

    return JobDescription(
        raw_text=cleaned_text,
        title=cleaned_title,
    )