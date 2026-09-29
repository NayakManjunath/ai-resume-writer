from ai_resume_writer.contracts.models import (
    CandidateProfile,
    GapItem,
    InformationStatus,
)


WEAK_EVIDENCE_PATTERNS = (
    "worked on",
    "worked with",
    "responsible for",
    "involved in",
    "helped with",
    "contributed to",
    "developed a ",
)


def _is_weak_evidence(text: str) -> bool:
    normalized = " ".join(text.lower().split())

    if not normalized:
        return False

    return any(
        pattern in normalized
        for pattern in WEAK_EVIDENCE_PATTERNS
    )


def _build_gap_item(evidence: str) -> GapItem:
    return GapItem(
        category="weak_evidence",
        item=evidence,
        reason=(
            "Your resume mentions this experience but does not provide "
            "enough detail about your contribution, approach, "
            "technologies, or context. Can you provide more details?"
        ),
        status=InformationStatus.DETECTED,
    )


def identify_weak_evidence(
    candidate_profile: CandidateProfile,
) -> list[GapItem]:
    """Identify vague experience and project evidence.

    The function only flags evidence using deterministic patterns.
    It does not infer or invent candidate information.
    """
    gaps: list[GapItem] = []
    seen: set[str] = set()

    evidence_items = [
        *candidate_profile.experience,
        *candidate_profile.projects,
    ]

    for evidence in evidence_items:
        normalized = " ".join(evidence.lower().split())

        if not normalized or normalized in seen:
            continue

        seen.add(normalized)

        if _is_weak_evidence(evidence):
            gaps.append(_build_gap_item(evidence))

    return gaps