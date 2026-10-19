
from ai_resume_writer.contracts.models import ResumeFormatChoice
from ai_resume_writer.formatting.decision import resolve_format_choice


def test_keep_existing_format_selection():
    result = resolve_format_choice(False)

    assert result == ResumeFormatChoice.KEEP_EXISTING


def test_professional_template_selection():
    result = resolve_format_choice(True)

    assert result == ResumeFormatChoice.USE_TEMPLATE


def test_format_choices_are_distinct():
    keep_existing = resolve_format_choice(False)
    use_template = resolve_format_choice(True)

    assert keep_existing != use_template
