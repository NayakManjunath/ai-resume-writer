from pathlib import Path

from docx import Document


class DocumentPreservationError(ValueError):
    """Raised when an existing DOCX cannot be preserved."""


def preserve_docx_format(
    source_path: Path,
    output_path: Path,
) -> Path:
    """Preserve an existing DOCX document as the formatting baseline."""
    source = Path(source_path)
    output = Path(output_path)

    if not source.exists():
        raise DocumentPreservationError(
            f"Source document does not exist: {source}"
        )

    if source.suffix.lower() != ".docx":
        raise DocumentPreservationError(
            "Existing format preservation currently supports DOCX files only."
        )

    try:
        document = Document(source)
        output.parent.mkdir(parents=True, exist_ok=True)
        document.save(output)
    except Exception as exc:
        raise DocumentPreservationError(
            f"Unable to preserve DOCX document: {source}"
        ) from exc

    return output