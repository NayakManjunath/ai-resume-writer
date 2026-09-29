from ai_resume_writer.contracts.models import (
    CandidateProfile,
    InformationStatus,
)

from ai_resume_writer.gap_analysis.weak_evidence import (
    identify_weak_evidence,
)


def test_detects_vague_experience_evidence():
    candidate = CandidateProfile(
        experience=[
            "Worked on machine learning models."
        ]
    )

    result = identify_weak_evidence(candidate)

    assert len(result) == 1
    assert result[0].category == "weak_evidence"
    assert result[0].item == "Worked on machine learning models."
    assert result[0].status == InformationStatus.DETECTED


def test_detects_vague_project_evidence():
    candidate = CandidateProfile(
        projects=[
            "Developed a machine learning project."
        ]
    )

    result = identify_weak_evidence(candidate)

    assert len(result) == 1
    assert result[0].category == "weak_evidence"
    assert result[0].item == "Developed a machine learning project."


def test_detailed_experience_does_not_create_weak_evidence_gap():
    candidate = CandidateProfile(
        experience=[
            (
                "Built a customer churn prediction model using Python "
                "and scikit-learn, achieving 0.87 F1 score."
            )
        ]
    )

    result = identify_weak_evidence(candidate)

    assert result == []


def test_detailed_project_does_not_create_weak_evidence_gap():
    candidate = CandidateProfile(
        projects=[
            (
                "Built a demand forecasting system using Python and "
                "XGBoost on historical sales data."
            )
        ]
    )

    result = identify_weak_evidence(candidate)

    assert result == []


def test_empty_experience_and_projects_return_no_gaps():
    candidate = CandidateProfile(
        experience=[],
        projects=[],
    )

    result = identify_weak_evidence(candidate)

    assert result == []


def test_blank_evidence_is_ignored():
    candidate = CandidateProfile(
        experience=[
            "",
            "   ",
        ],
        projects=[],
    )

    result = identify_weak_evidence(candidate)

    assert result == []


def test_weak_evidence_reason_requests_real_details():
    candidate = CandidateProfile(
        experience=[
            "Worked on data analysis."
        ]
    )

    result = identify_weak_evidence(candidate)

    assert len(result) == 1
    assert (
        "more details" in result[0].reason.lower()
        or "details" in result[0].reason.lower()
    )


def test_weak_evidence_does_not_invent_information():
    candidate = CandidateProfile(
        experience=[
            "Worked on machine learning models."
        ]
    )

    result = identify_weak_evidence(candidate)

    assert len(result) == 1
    assert "accuracy" not in result[0].reason.lower()
    assert "f1" not in result[0].reason.lower()
    assert "xgboost" not in result[0].reason.lower()


def test_duplicate_weak_evidence_is_not_reported_twice():
    candidate = CandidateProfile(
        experience=[
            "Worked on machine learning models.",
            "Worked on machine learning models.",
        ]
    )

    result = identify_weak_evidence(candidate)

    assert len(result) == 1


def test_clear_contribution_statement_is_not_flagged():
    candidate = CandidateProfile(
        experience=[
            (
                "Implemented automated document preprocessing using "
                "Python and reduced processing time by 35%."
            )
        ]
    )

    result = identify_weak_evidence(candidate)

    assert result == []