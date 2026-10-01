from ai_resume_writer.contracts.models import ResumeFormatChoice


def resolve_format_choice(change_format: bool) -> ResumeFormatChoice:
    """Resolve the user's explicit resume format preference.

    False means preserve the existing resume format.
    True means use the professional template.
    """
    if not isinstance(change_format, bool):
        raise TypeError("change_format must be a boolean.")

    if change_format:
        return ResumeFormatChoice.USE_TEMPLATE

    return ResumeFormatChoice.KEEP_EXISTING
