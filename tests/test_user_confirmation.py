from ai_resume_writer.contracts.models import (
    GapItem,
    InformationStatus,
    UserConfirmation,
)
from ai_resume_writer.gap_analysis.confirmation import (
    apply_user_confirmation,
)


def test_confirmed_gap_becomes_user_confirmed():
    gap = GapItem(
        category="missing_skill",
        item="Docker",
        reason=(
            "Docker appears relevant to the target role but was not "
            "found in your resume. Have you worked with Docker?"
        ),
    )

    confirmation = UserConfirmation(
        gap_item="Docker",
        confirmed=True,
        additional_information="Used Docker to package FastAPI applications.",
    )

    result = apply_user_confirmation(gap, confirmation)

    assert result.status == InformationStatus.USER_CONFIRMED


def test_confirmed_gap_preserves_user_information():
    gap = GapItem(
        category="missing_skill",
        item="Docker",
        reason="Have you worked with Docker?",
    )

    confirmation = UserConfirmation(
        gap_item="Docker",
        confirmed=True,
        additional_information="Used Docker for production deployments.",
    )

    result = apply_user_confirmation(gap, confirmation)

    assert result.item == "Docker"
    assert result.status == InformationStatus.USER_CONFIRMED


def test_rejected_gap_does_not_become_user_confirmed():
    gap = GapItem(
        category="missing_skill",
        item="Docker",
        reason="Have you worked with Docker?",
    )

    confirmation = UserConfirmation(
        gap_item="Docker",
        confirmed=False,
    )

    result = apply_user_confirmation(gap, confirmation)

    assert result.status == InformationStatus.DETECTED


def test_rejected_gap_does_not_accept_additional_information():
    gap = GapItem(
        category="missing_skill",
        item="Docker",
        reason="Have you worked with Docker?",
    )

    confirmation = UserConfirmation(
        gap_item="Docker",
        confirmed=False,
        additional_information="I used Docker extensively.",
    )

    result = apply_user_confirmation(gap, confirmation)

    assert result.status == InformationStatus.DETECTED


def test_confirmation_requires_matching_gap_item():
    gap = GapItem(
        category="missing_skill",
        item="Docker",
        reason="Have you worked with Docker?",
    )

    confirmation = UserConfirmation(
        gap_item="Python",
        confirmed=True,
        additional_information="Used Python professionally.",
    )

    try:
        apply_user_confirmation(gap, confirmation)
    except ValueError as exc:
        assert "gap item" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError for mismatched gap item")


def test_blank_gap_item_is_rejected_by_existing_contract():
    gap = GapItem(
        category="missing_skill",
        item="Docker",
        reason="Have you worked with Docker?",
    )

    confirmation = UserConfirmation(
        gap_item="",
        confirmed=True,
    )

    try:
        apply_user_confirmation(gap, confirmation)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for blank confirmation item")


def test_confirmed_gap_without_additional_information_can_be_confirmed():
    gap = GapItem(
        category="missing_skill",
        item="Docker",
        reason="Have you worked with Docker?",
    )

    confirmation = UserConfirmation(
        gap_item="Docker",
        confirmed=True,
    )

    result = apply_user_confirmation(gap, confirmation)

    assert result.status == InformationStatus.USER_CONFIRMED


def test_confirmation_does_not_change_gap_category():
    gap = GapItem(
        category="metric_opportunity",
        item="Improved processing efficiency.",
        reason="Can you provide a real metric?",
    )

    confirmation = UserConfirmation(
        gap_item="Improved processing efficiency.",
        confirmed=True,
        additional_information="Reduced processing time by 35%.",
    )

    result = apply_user_confirmation(gap, confirmation)

    assert result.category == "metric_opportunity"
    assert result.status == InformationStatus.USER_CONFIRMED


def test_confirmation_does_not_modify_gap_reason():
    gap = GapItem(
        category="weak_evidence",
        item="Worked on machine learning models.",
        reason="Can you provide more details?",
    )

    confirmation = UserConfirmation(
        gap_item="Worked on machine learning models.",
        confirmed=True,
        additional_information="Built classification models using Python.",
    )

    result = apply_user_confirmation(gap, confirmation)

    assert result.reason == "Can you provide more details?"


def test_confirmation_is_not_automatically_applied_without_user_input():
    gap = GapItem(
        category="missing_project",
        item="Projects",
        reason="Do you have a relevant project?",
    )

    # No confirmation object means the gap remains detected.
    assert gap.status == InformationStatus.DETECTED