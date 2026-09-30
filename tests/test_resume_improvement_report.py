from ai_resume_writer.contracts.models import (
    CandidateProfile,
    GapItem,
    InformationStatus,
    ResumeAnalysis,
    ResumeFormatChoice,
    TargetRole,
)
from ai_resume_writer.rewrite.improvement_report import (
    build_resume_improvement_report,
)


def build_candidate_profile() -> CandidateProfile:
    return CandidateProfile(
        name="Manjunath Naik",
        professional_summary="Data Scientist with experience building ML systems.",
        skills=[
            "Python",
            "SQL",
            "Machine Learning",
            "FastAPI",
        ],
        experience=[
            "Built machine learning services using Python and FastAPI.",
            "Improved document processing efficiency by 35%.",
        ],
        projects=[
            "Built a document intelligence system using NLP."
        ],
        education=[
            "Bachelor of Engineering"
        ],
        certifications=[
            "Data Science Certification"
        ],
    )


def build_analysis() -> ResumeAnalysis:
    return ResumeAnalysis(
        target_role=TargetRole(
            designation="Data Scientist",
            source="job_description",
        ),
        candidate_profile=build_candidate_profile(),
        gaps=[
            GapItem(
                category="missing_skill",
                item="Docker",
                reason=(
                    "Docker appears relevant to the target role but was not "
                    "found in your resume. Have you worked with Docker?"
                ),
                status=InformationStatus.DETECTED,
            ),
            GapItem(
                category="missing_section",
                item="Projects",
                reason=(
                    "Project experience appears relevant to the target role "
                    "but was not found in your resume. Do you have a "
                    "relevant project you would like to include?"
                ),
                status=InformationStatus.DETECTED,
            ),
            GapItem(
                category="weak_evidence",
                item="Worked on machine learning projects.",
                reason=(
                    "This experience may be strengthened with more detail."
                ),
                status=InformationStatus.DETECTED,
            ),
            GapItem(
                category="metric_opportunity",
                item="Improved document processing efficiency.",
                reason=(
                    "This achievement may be stronger with a real metric."
                ),
                status=InformationStatus.DETECTED,
            ),
        ],
    )


def test_report_contains_target_role():
    report = build_resume_improvement_report(
        analysis=build_analysis(),
        format_choice=ResumeFormatChoice.KEEP_EXISTING,
    )

    assert report.target_role.designation == "Data Scientist"


def test_report_contains_information_found():
    report = build_resume_improvement_report(
        analysis=build_analysis(),
        format_choice=ResumeFormatChoice.KEEP_EXISTING,
    )

    summary = " ".join(report.improvement_summary)

    assert "Python" in summary
    assert "SQL" in summary
    assert "Machine Learning" in summary


def test_report_contains_potential_gaps():
    report = build_resume_improvement_report(
        analysis=build_analysis(),
        format_choice=ResumeFormatChoice.KEEP_EXISTING,
    )

    summary = " ".join(report.improvement_summary)

    assert "Docker" in summary


def test_report_contains_missing_sections():
    report = build_resume_improvement_report(
        analysis=build_analysis(),
        format_choice=ResumeFormatChoice.KEEP_EXISTING,
    )

    summary = " ".join(report.improvement_summary)

    assert "Projects" in summary


def test_report_contains_additional_information_requested():
    report = build_resume_improvement_report(
        analysis=build_analysis(),
        format_choice=ResumeFormatChoice.KEEP_EXISTING,
    )

    summary = " ".join(report.improvement_summary)

    assert "Have you worked with Docker?" in summary


def test_report_contains_format_choice():
    report = build_resume_improvement_report(
        analysis=build_analysis(),
        format_choice=ResumeFormatChoice.USE_TEMPLATE,
    )

    assert report.format_choice == ResumeFormatChoice.USE_TEMPLATE

    summary = " ".join(report.improvement_summary)

    assert "template" in summary.lower()


def test_report_preserves_original_candidate_profile():
    analysis = build_analysis()
    original_profile = analysis.candidate_profile.model_copy(deep=True)

    report = build_resume_improvement_report(
        analysis=analysis,
        format_choice=ResumeFormatChoice.KEEP_EXISTING,
    )

    assert report.original_profile == original_profile


def test_report_does_not_fabricate_missing_information():
    report = build_resume_improvement_report(
        analysis=build_analysis(),
        format_choice=ResumeFormatChoice.KEEP_EXISTING,
    )

    assert "Docker" not in report.original_profile.skills
    assert "Docker" not in report.improved_sections.get("skills", [])


def test_report_preserves_detected_gap_status():
    analysis = build_analysis()

    report = build_resume_improvement_report(
        analysis=analysis,
        format_choice=ResumeFormatChoice.KEEP_EXISTING,
    )

    assert any(
        "Docker" in item
        for item in report.improvement_summary
    )


def test_report_is_deterministic():
    analysis = build_analysis()

    report_one = build_resume_improvement_report(
        analysis=analysis,
        format_choice=ResumeFormatChoice.KEEP_EXISTING,
    )

    report_two = build_resume_improvement_report(
        analysis=analysis,
        format_choice=ResumeFormatChoice.KEEP_EXISTING,
    )

    assert report_one == report_two


def test_report_does_not_modify_analysis():
    analysis = build_analysis()
    original_analysis = analysis.model_copy(deep=True)

    build_resume_improvement_report(
        analysis=analysis,
        format_choice=ResumeFormatChoice.KEEP_EXISTING,
    )

    assert analysis == original_analysis