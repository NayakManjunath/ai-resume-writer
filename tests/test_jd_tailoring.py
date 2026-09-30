from ai_resume_writer.contracts.models import (
    CandidateProfile,
    JobDescription,
    TargetRole,
)
from ai_resume_writer.rewrite.tailoring import tailor_resume


def test_tailoring_emphasizes_candidate_skills_relevant_to_jd(monkeypatch):
    profile = CandidateProfile(
        skills=[
            "Python",
            "SQL",
            "Machine Learning",
        ],
        experience=[
            "Built machine learning models using Python and SQL.",
        ],
    )

    job_description = JobDescription(
        raw_text="Data Scientist role requiring Python, SQL and Machine Learning.",
        title="Data Scientist",
        required_skills=[
            "Python",
            "SQL",
            "Machine Learning",
        ],
    )

    target_role = TargetRole(
        designation="Data Scientist",
        source="jd",
    )

    monkeypatch.setattr(
        "ai_resume_writer.rewrite.tailoring._generate_tailored_rewrite",
        lambda *args, **kwargs: {
            "skills": [
                "Python",
                "SQL",
                "Machine Learning",
            ],
            "experience": [
                "Built machine learning models using Python and SQL."
            ],
        },
    )

    result = tailor_resume(
        candidate_profile=profile,
        job_description=job_description,
        target_role=target_role,
    )

    assert result.improved_sections["skills"] == [
        "Python",
        "SQL",
        "Machine Learning",
    ]


def test_tailoring_does_not_add_jd_skill_missing_from_candidate(monkeypatch):
    profile = CandidateProfile(
        skills=["Python"],
        experience=[
            "Built machine learning models using Python.",
        ],
    )

    job_description = JobDescription(
        raw_text="Data Scientist role requiring Python, Docker and AWS.",
        title="Data Scientist",
        required_skills=[
            "Python",
            "Docker",
            "AWS",
        ],
    )

    target_role = TargetRole(
        designation="Data Scientist",
        source="jd",
    )

    monkeypatch.setattr(
        "ai_resume_writer.rewrite.tailoring._generate_tailored_rewrite",
        lambda *args, **kwargs: {
            "skills": [
                "Python",
                "Docker",
                "AWS",
            ],
        },
    )

    result = tailor_resume(
        candidate_profile=profile,
        job_description=job_description,
        target_role=target_role,
    )

    assert result.improved_sections["skills"] == ["Python"]


def test_tailoring_does_not_create_missing_project(monkeypatch):
    profile = CandidateProfile(
        skills=["Python"],
        projects=[],
    )

    job_description = JobDescription(
        raw_text="Data Scientist role requiring recommendation system projects.",
        title="Data Scientist",
    )

    target_role = TargetRole(
        designation="Data Scientist",
        source="jd",
    )

    monkeypatch.setattr(
        "ai_resume_writer.rewrite.tailoring._generate_tailored_rewrite",
        lambda *args, **kwargs: {
            "projects": [
                "Built a recommendation system using Python."
            ],
        },
    )

    result = tailor_resume(
        candidate_profile=profile,
        job_description=job_description,
        target_role=target_role,
    )

    assert result.improved_sections["projects"] == []


def test_tailoring_does_not_invent_metrics(monkeypatch):
    profile = CandidateProfile(
        experience=[
            "Built machine learning models using Python.",
        ],
    )

    job_description = JobDescription(
        raw_text="Data Scientist role focused on machine learning.",
        title="Data Scientist",
    )

    target_role = TargetRole(
        designation="Data Scientist",
        source="jd",
    )

    monkeypatch.setattr(
        "ai_resume_writer.rewrite.tailoring._generate_tailored_rewrite",
        lambda *args, **kwargs: {
            "experience": [
                (
                    "Built machine learning models using Python "
                    "with 95% accuracy."
                ),
            ],
        },
    )

    result = tailor_resume(
        candidate_profile=profile,
        job_description=job_description,
        target_role=target_role,
    )

    assert "95%" not in " ".join(
        result.improved_sections.get("experience", [])
    )


def test_tailoring_preserves_original_profile(monkeypatch):
    profile = CandidateProfile(
        skills=["Python"],
        experience=[
            "Built machine learning models using Python.",
        ],
    )

    job_description = JobDescription(
        raw_text="Data Scientist role requiring Python.",
        title="Data Scientist",
        required_skills=["Python"],
    )

    target_role = TargetRole(
        designation="Data Scientist",
        source="jd",
    )

    monkeypatch.setattr(
        "ai_resume_writer.rewrite.tailoring._generate_tailored_rewrite",
        lambda *args, **kwargs: {
            "skills": ["Python"],
            "experience": [
                "Developed machine learning models using Python."
            ],
        },
    )

    result = tailor_resume(
        candidate_profile=profile,
        job_description=job_description,
        target_role=target_role,
    )

    assert result.original_profile == profile


def test_tailoring_preserves_target_role(monkeypatch):
    profile = CandidateProfile(
        skills=["Python"],
    )

    job_description = JobDescription(
        raw_text="Data Scientist role requiring Python.",
        title="Data Scientist",
        required_skills=["Python"],
    )

    target_role = TargetRole(
        designation="Data Scientist",
        source="jd",
    )

    monkeypatch.setattr(
        "ai_resume_writer.rewrite.tailoring._generate_tailored_rewrite",
        lambda *args, **kwargs: {
            "skills": ["Python"],
        },
    )

    result = tailor_resume(
        candidate_profile=profile,
        job_description=job_description,
        target_role=target_role,
    )

    assert result.target_role == target_role


def test_tailoring_uses_jd_alignment_to_restrict_missing_skills(
    monkeypatch,
):
    profile = CandidateProfile(
        skills=[
            "Python",
            "SQL",
        ],
    )

    job_description = JobDescription(
        raw_text="Data Scientist role requiring Python, SQL and Docker.",
        title="Data Scientist",
        required_skills=[
            "Python",
            "SQL",
            "Docker",
        ],
    )

    target_role = TargetRole(
        designation="Data Scientist",
        source="jd",
    )

    captured = {}

    def fake_generate(*args, **kwargs):
        captured["job_description"] = args[1]
        return {
            "skills": [
                "Python",
                "SQL",
            ],
        }

    monkeypatch.setattr(
        "ai_resume_writer.rewrite.tailoring._generate_tailored_rewrite",
        fake_generate,
    )

    result = tailor_resume(
        candidate_profile=profile,
        job_description=job_description,
        target_role=target_role,
    )

    assert captured["job_description"] == job_description
    assert result.improved_sections["skills"] == [
        "Python",
        "SQL",
    ]