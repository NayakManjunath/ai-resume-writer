from ai_resume_writer.contracts.models import (
    CandidateProfile,
    InformationStatus,
)
from ai_resume_writer.gap_analysis.metrics import (
    identify_metric_opportunities,
)


def test_detects_improvement_without_metric():
    candidate = CandidateProfile(
        experience=[
            "Improved document processing efficiency."
        ]
    )

    result = identify_metric_opportunities(candidate)

    assert len(result) == 1
    assert result[0].category == "metric_opportunity"
    assert result[0].item == "Improved document processing efficiency."
    assert result[0].status == InformationStatus.DETECTED


def test_detects_performance_claim_without_metric():
    candidate = CandidateProfile(
        experience=[
            "Improved model performance."
        ]
    )

    result = identify_metric_opportunities(candidate)

    assert len(result) == 1
    assert result[0].category == "metric_opportunity"


def test_detects_efficiency_claim_without_metric():
    candidate = CandidateProfile(
        projects=[
            "Optimized the data processing pipeline for better efficiency."
        ]
    )

    result = identify_metric_opportunities(candidate)

    assert len(result) == 1
    assert result[0].category == "metric_opportunity"


def test_metric_opportunity_reason_requests_real_metric():
    candidate = CandidateProfile(
        experience=[
            "Reduced processing time."
        ]
    )

    result = identify_metric_opportunities(candidate)

    assert len(result) == 1
    assert "real" in result[0].reason.lower()
    assert "metric" in result[0].reason.lower()


def test_existing_percentage_metric_is_not_flagged():
    candidate = CandidateProfile(
        experience=[
            "Improved document processing efficiency by 35%."
        ]
    )

    result = identify_metric_opportunities(candidate)

    assert result == []


def test_existing_time_metric_is_not_flagged():
    candidate = CandidateProfile(
        experience=[
            "Reduced processing time from 10 minutes to 6 minutes."
        ]
    )

    result = identify_metric_opportunities(candidate)

    assert result == []


def test_existing_scale_metric_is_not_flagged():
    candidate = CandidateProfile(
        projects=[
            "Built a pipeline processing 10,000 documents per month."
        ]
    )

    result = identify_metric_opportunities(candidate)

    assert result == []


def test_non_achievement_statement_is_not_flagged():
    candidate = CandidateProfile(
        experience=[
            "Used Python and Pandas for data analysis."
        ]
    )

    result = identify_metric_opportunities(candidate)

    assert result == []


def test_empty_experience_and_projects_return_no_gaps():
    candidate = CandidateProfile(
        experience=[],
        projects=[],
    )

    result = identify_metric_opportunities(candidate)

    assert result == []


def test_duplicate_metric_opportunities_are_not_reported_twice():
    candidate = CandidateProfile(
        experience=[
            "Improved system performance.",
            "Improved system performance.",
        ]
    )

    result = identify_metric_opportunities(candidate)

    assert len(result) == 1


def test_metric_detection_does_not_invent_numbers():
    candidate = CandidateProfile(
        experience=[
            "Improved system performance."
        ]
    )

    result = identify_metric_opportunities(candidate)

    assert len(result) == 1
    assert "35%" not in result[0].reason
    assert "50%" not in result[0].reason
    assert "2x" not in result[0].reason.lower()