
from ai_resume_writer.contracts.models import (
    JobDescription,
    ResumeDocument,
)
from ai_resume_writer.ui.analysis_page import build_resume_analysis


def test_analysis_includes_jd_alignment_and_gap_checks():
    resume = ResumeDocument(
        file_name="resume.docx",
        file_type="docx",
        raw_text=(
            "Candidate Name\n"
            "Experience\n"
            "Data Analyst\n"
            "Worked on Python automation\n"
            "Skills\n"
            "Python\n"
            "Projects\n"
            "Sales Dashboard\n"
            "Education\n"
            "BSc Computer Science\n"
        ),
    )
    jd = JobDescription(
        raw_text=(
            "Data Scientist\n"
            "Required Skills:\n"
            "Python\n"
            "SQL\n"
            "Preferred Skills:\n"
            "Docker\n"
        ),
        title="Data Scientist",
        required_skills=["Python", "SQL"],
        preferred_skills=["Docker"],
    )

    analysis, alignment = build_resume_analysis(
        resume=resume,
        job_description=jd,
    )

    assert analysis.target_role.designation == "Data Scientist"
    assert analysis.target_role.source == "jd"
    assert alignment is not None
    assert alignment.matched_required_skills == ["Python"]
    assert alignment.missing_required_skills == ["SQL"]
    assert alignment.missing_preferred_skills == ["Docker"]
    assert any(gap.category == "weak_evidence" for gap in analysis.gaps)


def test_resume_only_analysis_does_not_run_jd_checks():
    resume = ResumeDocument(
        file_name="resume.docx",
        file_type="docx",
        raw_text=(
            "Candidate Name\n"
            "Experience\n"
            "Data Analyst\n"
            "Improved reporting workflows\n"
            "Skills\n"
            "Python\n"
        ),
    )

    analysis, alignment = build_resume_analysis(
        resume=resume,
        job_description=None,
    )

    assert analysis.target_role.designation == "Data Analyst"
    assert analysis.target_role.source == "resume"
    assert alignment is None
    assert not any(
        gap.category in {
            "required_skill",
            "preferred_skill",
            "missing_project",
            "missing_section",
        }
        for gap in analysis.gaps
    )


def test_explicit_designation_takes_priority():
    resume = ResumeDocument(
        file_name="resume.docx",
        file_type="docx",
        raw_text="Candidate Name\nExperience\nData Analyst\n",
    )
    jd = JobDescription(
        raw_text="Data Scientist\n",
        title="Data Scientist",
    )

    analysis, _ = build_resume_analysis(
        resume=resume,
        job_description=jd,
        user_designation="Machine Learning Engineer",
    )

    assert analysis.target_role.designation == "Machine Learning Engineer"
    assert analysis.target_role.source == "user"


def test_missing_role_requires_user_input():
    resume = ResumeDocument(
        file_name="resume.docx",
        file_type="docx",
        raw_text="Candidate Name\nSkills\nPython\n",
    )

    try:
        build_resume_analysis(
            resume=resume,
            job_description=None,
        )
    except ValueError as exc:
        assert "target designation" in str(exc).lower()
    else:
        raise AssertionError("Expected missing target designation to fail.")
