from datetime import date

from ai_resume_writer.contracts.models import CandidateProfile
from ai_resume_writer.resume.experience import (
    calculate_experience_years,
)


def test_calculates_years_from_year_range() -> None:
    profile = CandidateProfile(
        experience=[
            "Data Scientist | ABC Technologies | 2022-2024",
        ],
    )

    result = calculate_experience_years(
        profile,
        as_of=date(2024, 12, 31),
    )

    assert result.experience_years == 3.0


def test_calculates_present_using_as_of_date() -> None:
    profile = CandidateProfile(
        experience=[
            "Data Scientist | ABC Technologies | 2024-Present",
        ],
    )

    result = calculate_experience_years(
        profile,
        as_of=date(2026, 1, 1),
    )

    assert result.experience_years == 2.08


def test_calculates_month_year_range() -> None:
    profile = CandidateProfile(
        experience=[
            "Data Scientist | ABC Technologies | Jan 2022-Mar 2024",
        ],
    )

    result = calculate_experience_years(
        profile,
        as_of=date(2024, 3, 1),
    )

    assert result.experience_years == 2.25


def test_overlapping_employment_periods_are_not_double_counted() -> None:
    profile = CandidateProfile(
        experience=[
            "Data Scientist | Company A | 2022-2024",
            "ML Engineer | Company B | 2023-2025",
        ],
    )

    result = calculate_experience_years(
        profile,
        as_of=date(2025, 1, 1),
    )

    assert result.experience_years == 4.0


def test_missing_dates_return_none() -> None:
    profile = CandidateProfile(
        experience=[
            "Data Scientist - Test Company",
        ],
    )

    result = calculate_experience_years(profile)

    assert result.experience_years is None


def test_invalid_date_range_is_not_used() -> None:
    profile = CandidateProfile(
        experience=[
            "Data Scientist | ABC Technologies | 2025-2022",
        ],
    )

    result = calculate_experience_years(
        profile,
        as_of=date(2026, 1, 1),
    )

    assert result.experience_years is None


def test_non_date_experience_bullets_do_not_create_experience() -> None:
    profile = CandidateProfile(
        experience=[
            "Data Scientist | ABC Technologies | 2024-2025",
            "Built forecasting models.",
            "Improved processing performance.",
        ],
    )

    result = calculate_experience_years(
        profile,
        as_of=date(2025, 1, 1),
    )

    assert result.experience_years == 2.0