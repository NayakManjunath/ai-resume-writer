import re

from ai_resume_writer.contracts.models import (
    CandidateProfile,
    GapItem,
    InformationStatus,
)


METRIC_PATTERNS = (
    r"\b\d+(?:\.\d+)?\s*%",
    r"\b\d+(?:\.\d+)?\s*x\b",
    r"\b\d[\d,]*\s+(?:users|documents|records|requests|transactions|projects)\b",
    r"\b\d+(?:\.\d+)?\s*(?:seconds?|minutes?|hours?|days?|months?|years?)\b",
)

OPPORTUNITY_PATTERNS = (
    "improved",
    "improve",
    "increased",
    "increase",
    "reduced",
    "reduce",
    "decreased",
    "decrease",
    "optimized",
    "optimize",
    "enhanced",
    "enhance",
    "accelerated",
    "accelerate",
    "saved",
    "saving",
    "grew",
    "growth",
    "boosted",
    "boost",
)


def _contains_metric(text: str) -> bool:
    return any(
        re.search(pattern, text, flags=re.IGNORECASE)
        for pattern in METRIC_PATTERNS
    )


def _contains_opportunity(text: str) -> bool:
    normalized = " ".join(text.lower().split())

    if not normalized:
        return False

    return any(
        opportunity in normalized
        for opportunity in OPPORTUNITY_PATTERNS
    )


def _build_gap_item(evidence: str) -> GapItem:
    return GapItem(
        category="metric_opportunity",
        item=evidence,
        reason=(
            "This resume statement describes an achievement or impact "
            "but does not include a measurable result. If available, "
            "what real metric can you provide to support this claim?"
        ),
        status=InformationStatus.DETECTED,
    )


def identify_metric_opportunities(
    candidate_profile: CandidateProfile,
) -> list[GapItem]:
    """Identify achievement statements that lack measurable evidence.

    The function never estimates or invents metrics. It only identifies
    statements that may benefit from a real metric supplied by the user.
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

        if _contains_opportunity(evidence) and not _contains_metric(evidence):
            gaps.append(_build_gap_item(evidence))

    return gaps