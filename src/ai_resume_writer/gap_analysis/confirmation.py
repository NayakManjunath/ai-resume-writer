from ai_resume_writer.contracts.models import (
    GapItem,
    InformationStatus,
    UserConfirmation,
)


def apply_user_confirmation(
    gap: GapItem,
    confirmation: UserConfirmation,
) -> GapItem:
    """Apply explicit user confirmation to a detected gap.

    A gap becomes USER_CONFIRMED only when the confirmation explicitly
    confirms the same gap item. Rejected confirmations leave the gap
    detected and do not introduce user information.
    """
    if not confirmation.gap_item.strip():
        raise ValueError("Gap item cannot be blank.")

    if confirmation.gap_item.strip() != gap.item.strip():
        raise ValueError("Confirmation gap item does not match the gap item.")

    if not confirmation.confirmed:
        return gap.model_copy(
            update={
                "status": InformationStatus.DETECTED,
            }
        )

    return gap.model_copy(
        update={
            "status": InformationStatus.USER_CONFIRMED,
        }
    )