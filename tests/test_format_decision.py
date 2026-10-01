import pytest

from ai_resume_writer.contracts.models import ResumeFormatChoice
from ai_resume_writer.formatting.decision import resolve_format_choice


def test_keep_existing_format():
    result = resolve_format_choice(False)

    assert result == ResumeFormatChoice.KEEP_EXISTING


def test_use_template_format():
    result = resolve_format_choice(True)

    assert result == ResumeFormatChoice.USE_TEMPLATE


@pytest.mark.parametrize("value", [None, 0, 1, "yes", "no", []])
def test_invalid_format_choice_input(value):
    with pytest.raises(TypeError):
        resolve_format_choice(value)
