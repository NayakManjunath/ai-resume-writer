from dataclasses import dataclass
from datetime import date
import re

from ai_resume_writer.contracts.models import CandidateProfile


class ExperienceCalculationError(ValueError):
    """Raised when experience calculation input is invalid."""


@dataclass(frozen=True)
class EmploymentPeriod:
    """Normalized employment period with its date precision."""

    start: date
    end: date
    precision: str


DATE_RANGE_PATTERN = re.compile(
    r"(?P<start>"
    r"(?:"
    r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
    r"(?:uary|ruary|ch|il|e|y|ust|tember|ober|ember)?"
    r"\s+)?"
    r"\d{4}"
    r")"
    r"\s*[-–—]\s*"
    r"(?P<end>"
    r"(?:"
    r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
    r"(?:uary|ruary|ch|il|e|y|ust|tember|ober|ember)?"
    r"\s+)?"
    r"(?:\d{4}|Present|present|CURRENT|current)"
    r")"
)


MONTH_NAMES = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}


def _parse_date(
    value: str,
    *,
    as_of: date,
) -> tuple[date, str] | None:
    """Parse a supported date and preserve its precision."""
    cleaned = value.strip()

    if cleaned.lower() in {"present", "current"}:
        return as_of, "month"

    month_match = re.fullmatch(
        r"([A-Za-z]+)\s+(\d{4})",
        cleaned,
    )

    if month_match:
        month_name = month_match.group(1).lower()
        year = int(month_match.group(2))
        month = MONTH_NAMES.get(month_name)

        if month is None:
            return None

        return date(year, month, 1), "month"

    if re.fullmatch(r"\d{4}", cleaned):
        return date(int(cleaned), 1, 1), "year"

    return None


def _extract_periods(
    experience: list[str],
    *,
    as_of: date,
) -> list[EmploymentPeriod]:
    """Extract valid employment periods from experience evidence."""
    periods: list[EmploymentPeriod] = []

    for item in experience:
        match = DATE_RANGE_PATTERN.search(item)

        if not match:
            continue

        start_result = _parse_date(
            match.group("start"),
            as_of=as_of,
        )
        end_result = _parse_date(
            match.group("end"),
            as_of=as_of,
        )

        if start_result is None or end_result is None:
            continue

        start, start_precision = start_result
        end, end_precision = end_result

        if end < start:
            continue

        precision = (
            "year"
            if start_precision == "year"
            and end_precision == "year"
            else "month"
        )

        periods.append(
            EmploymentPeriod(
                start=start,
                end=end,
                precision=precision,
            )
        )

    return periods


def _merge_periods(
    periods: list[EmploymentPeriod],
) -> list[EmploymentPeriod]:
    """Merge overlapping employment periods."""
    if not periods:
        return []

    sorted_periods = sorted(
        periods,
        key=lambda period: period.start,
    )

    merged: list[EmploymentPeriod] = [sorted_periods[0]]

    for current in sorted_periods[1:]:
        previous = merged[-1]

        if current.start <= previous.end:
            precision = (
                "year"
                if previous.precision == "year"
                and current.precision == "year"
                else "month"
            )

            merged[-1] = EmploymentPeriod(
                start=previous.start,
                end=max(previous.end, current.end),
                precision=precision,
            )
        else:
            merged.append(current)

    return merged


def _calculate_period_years(
    period: EmploymentPeriod,
) -> float:
    """Calculate years according to the period precision."""
    if period.precision == "year":
        return float(
            period.end.year - period.start.year + 1
        )

    total_months = (
        (period.end.year - period.start.year) * 12
        + (period.end.month - period.start.month)
        + 1
    )

    return total_months / 12


def calculate_experience_years(
    candidate_profile: CandidateProfile,
    *,
    as_of: date | None = None,
) -> CandidateProfile:
    """Calculate professional experience from explicit dates."""
    calculation_date = as_of or date.today()

    periods = _extract_periods(
        candidate_profile.experience,
        as_of=calculation_date,
    )

    if not periods:
        return candidate_profile.model_copy(
            update={"experience_years": None}
        )

    merged_periods = _merge_periods(periods)

    experience_years = round(
        sum(
            _calculate_period_years(period)
            for period in merged_periods
        ),
        2,
    )

    return candidate_profile.model_copy(
        update={"experience_years": experience_years}
    )