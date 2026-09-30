from ai_resume_writer.contracts.models import CandidateProfile, TargetRole
from ai_resume_writer.rewrite.resume import rewrite_resume


def _mock_identity_rewrite(candidate_profile, target_role):
    """Return candidate evidence unchanged for deterministic unit tests."""
    return {
        "professional_summary": (
            [candidate_profile.professional_summary]
            if candidate_profile.professional_summary
            else []
        ),
        "skills": list(candidate_profile.skills),
        "experience": list(candidate_profile.experience),
        "projects": list(candidate_profile.projects),
        "education": list(candidate_profile.education),
        "certifications": list(candidate_profile.certifications),
    }


def test_rewrite_preserves_target_role(monkeypatch):
    profile = CandidateProfile(
        professional_summary="Data scientist with experience in Python.",
        skills=["Python", "SQL"],
        experience=["Built data analysis workflows using Python."],
    )

    target_role = TargetRole(
        designation="Data Scientist",
        source="user",
    )

    monkeypatch.setattr(
        "ai_resume_writer.rewrite.resume._generate_rewrite",
        _mock_identity_rewrite,
    )

    result = rewrite_resume(
        candidate_profile=profile,
        target_role=target_role,
    )

    assert result.target_role.designation == "Data Scientist"


def test_rewrite_preserves_existing_skills(monkeypatch):
    profile = CandidateProfile(
        skills=["Python", "SQL", "Pandas"],
    )

    target_role = TargetRole(
        designation="Data Scientist",
        source="user",
    )

    monkeypatch.setattr(
        "ai_resume_writer.rewrite.resume._generate_rewrite",
        _mock_identity_rewrite,
    )

    result = rewrite_resume(
        candidate_profile=profile,
        target_role=target_role,
    )

    assert result.original_profile.skills == [
        "Python",
        "SQL",
        "Pandas",
    ]


def test_rewrite_preserves_existing_experience(monkeypatch):
    experience = [
        "Built data analysis workflows using Python.",
        "Created machine learning models.",
    ]

    profile = CandidateProfile(
        experience=experience,
    )

    target_role = TargetRole(
        designation="Data Scientist",
        source="user",
    )

    monkeypatch.setattr(
        "ai_resume_writer.rewrite.resume._generate_rewrite",
        _mock_identity_rewrite,
    )

    result = rewrite_resume(
        candidate_profile=profile,
        target_role=target_role,
    )

    assert result.original_profile.experience == experience


def test_rewrite_preserves_existing_projects(monkeypatch):
    projects = [
        "Built a sales forecasting project using Python.",
    ]

    profile = CandidateProfile(
        projects=projects,
    )

    target_role = TargetRole(
        designation="Data Scientist",
        source="user",
    )

    monkeypatch.setattr(
        "ai_resume_writer.rewrite.resume._generate_rewrite",
        _mock_identity_rewrite,
    )

    result = rewrite_resume(
        candidate_profile=profile,
        target_role=target_role,
    )

    assert result.original_profile.projects == projects


def test_rewrite_does_not_create_missing_skills(monkeypatch):
    profile = CandidateProfile(
        skills=["Python"],
    )

    target_role = TargetRole(
        designation="Data Scientist",
        source="user",
    )

    monkeypatch.setattr(
        "ai_resume_writer.rewrite.resume._generate_rewrite",
        lambda *args, **kwargs: {
            "skills": [
                "Python",
                "TensorFlow",
                "PyTorch",
            ],
        },
    )

    result = rewrite_resume(
        candidate_profile=profile,
        target_role=target_role,
    )

    assert result.improved_sections["skills"] == ["Python"]


def test_rewrite_does_not_create_missing_projects(monkeypatch):
    profile = CandidateProfile(
        skills=["Python"],
        projects=[],
    )

    target_role = TargetRole(
        designation="Data Scientist",
        source="user",
    )

    monkeypatch.setattr(
        "ai_resume_writer.rewrite.resume._generate_rewrite",
        lambda *args, **kwargs: {
            "projects": [
                "Built a recommendation system.",
            ],
        },
    )

    result = rewrite_resume(
        candidate_profile=profile,
        target_role=target_role,
    )

    assert result.improved_sections["projects"] == []


def test_rewrite_does_not_create_missing_metrics(monkeypatch):
    profile = CandidateProfile(
        experience=[
            "Built machine learning models using Python.",
        ],
    )

    target_role = TargetRole(
        designation="Data Scientist",
        source="user",
    )

    monkeypatch.setattr(
        "ai_resume_writer.rewrite.resume._generate_rewrite",
        lambda *args, **kwargs: {
            "experience": [
                (
                    "Built machine learning models using Python "
                    "with 95% accuracy and improved performance by 40%."
                ),
            ],
        },
    )

    result = rewrite_resume(
        candidate_profile=profile,
        target_role=target_role,
    )

    rewritten_text = " ".join(
        value
        for values in result.improved_sections.values()
        for value in values
    )

    assert "95%" not in rewritten_text
    assert "40%" not in rewritten_text


def test_empty_profile_is_handled_safely(monkeypatch):
    profile = CandidateProfile()

    target_role = TargetRole(
        designation="Data Scientist",
        source="user",
    )

    monkeypatch.setattr(
        "ai_resume_writer.rewrite.resume._generate_rewrite",
        _mock_identity_rewrite,
    )

    result = rewrite_resume(
        candidate_profile=profile,
        target_role=target_role,
    )

    assert result.original_profile == profile
    assert result.improved_sections == {}


def test_rewrite_result_contains_structured_sections(monkeypatch):
    profile = CandidateProfile(
        professional_summary="Data scientist with Python experience.",
        skills=["Python"],
        experience=["Built data analysis workflows."],
    )

    target_role = TargetRole(
        designation="Data Scientist",
        source="user",
    )

    monkeypatch.setattr(
        "ai_resume_writer.rewrite.resume._generate_rewrite",
        _mock_identity_rewrite,
    )

    result = rewrite_resume(
        candidate_profile=profile,
        target_role=target_role,
    )

    assert isinstance(result.improved_sections, dict)


def test_rewrite_keeps_original_profile_separate_from_improvements(
    monkeypatch,
):
    profile = CandidateProfile(
        professional_summary="Data scientist with Python experience.",
        skills=["Python"],
    )

    target_role = TargetRole(
        designation="Data Scientist",
        source="user",
    )

    monkeypatch.setattr(
        "ai_resume_writer.rewrite.resume._generate_rewrite",
        _mock_identity_rewrite,
    )

    result = rewrite_resume(
        candidate_profile=profile,
        target_role=target_role,
    )

    assert result.original_profile is not profile
    assert result.original_profile == profile


def test_rewrite_improves_existing_experience_wording(monkeypatch):
    profile = CandidateProfile(
        experience=[
            "Worked on machine learning models using Python.",
        ],
    )

    target_role = TargetRole(
        designation="Data Scientist",
        source="user",
    )

    def fake_llm_rewrite(*args, **kwargs):
        return {
            "experience": [
                "Developed machine learning models using Python.",
            ],
        }

    monkeypatch.setattr(
        "ai_resume_writer.rewrite.resume._generate_rewrite",
        fake_llm_rewrite,
    )

    result = rewrite_resume(
        candidate_profile=profile,
        target_role=target_role,
    )

    assert result.improved_sections["experience"] == [
        "Developed machine learning models using Python.",
    ]


def test_rewrite_uses_existing_candidate_evidence(monkeypatch):
    profile = CandidateProfile(
        experience=[
            "Built machine learning models using Python and Pandas.",
        ],
    )

    target_role = TargetRole(
        designation="Data Scientist",
        source="user",
    )

    captured_input = {}

    def fake_llm_rewrite(candidate_profile, target_role):
        captured_input["experience"] = candidate_profile.experience
        captured_input["designation"] = target_role.designation

        return {
            "experience": [
                "Built machine learning models using Python and Pandas.",
            ],
        }

    monkeypatch.setattr(
        "ai_resume_writer.rewrite.resume._generate_rewrite",
        fake_llm_rewrite,
    )

    rewrite_resume(
        candidate_profile=profile,
        target_role=target_role,
    )

    assert captured_input["experience"] == [
        "Built machine learning models using Python and Pandas.",
    ]

    assert captured_input["designation"] == "Data Scientist"


def test_rewrite_preserves_original_profile_when_llm_rewrites_content(
    monkeypatch,
):
    original_experience = [
        "Worked on machine learning models using Python.",
    ]

    profile = CandidateProfile(
        experience=original_experience,
    )

    target_role = TargetRole(
        designation="Data Scientist",
        source="user",
    )

    def fake_llm_rewrite(*args, **kwargs):
        return {
            "experience": [
                "Developed machine learning models using Python.",
            ],
        }

    monkeypatch.setattr(
        "ai_resume_writer.rewrite.resume._generate_rewrite",
        fake_llm_rewrite,
    )

    result = rewrite_resume(
        candidate_profile=profile,
        target_role=target_role,
    )

    assert result.original_profile.experience == original_experience

    assert result.improved_sections["experience"] != original_experience


def test_rewrite_does_not_accept_unsupported_llm_section(
    monkeypatch,
):
    profile = CandidateProfile(
        experience=[
            "Built machine learning models using Python.",
        ],
    )

    target_role = TargetRole(
        designation="Data Scientist",
        source="user",
    )

    def fake_llm_rewrite(*args, **kwargs):
        return {
            "experience": [
                "Built machine learning models using Python.",
            ],
            "skills": [
                "Python",
                "TensorFlow",
            ],
        }

    monkeypatch.setattr(
        "ai_resume_writer.rewrite.resume._generate_rewrite",
        fake_llm_rewrite,
    )

    result = rewrite_resume(
        candidate_profile=profile,
        target_role=target_role,
    )

    assert result.improved_sections["skills"] == []


def test_rewrite_does_not_add_unsupported_metric(
    monkeypatch,
):
    profile = CandidateProfile(
        experience=[
            "Built machine learning models using Python.",
        ],
    )

    target_role = TargetRole(
        designation="Data Scientist",
        source="user",
    )

    def fake_llm_rewrite(*args, **kwargs):
        return {
            "experience": [
                (
                    "Built machine learning models using Python "
                    "with 95% accuracy."
                ),
            ],
        }

    monkeypatch.setattr(
        "ai_resume_writer.rewrite.resume._generate_rewrite",
        fake_llm_rewrite,
    )

    result = rewrite_resume(
        candidate_profile=profile,
        target_role=target_role,
    )

    rewritten_experience = result.improved_sections["experience"]

    assert "95%" not in " ".join(rewritten_experience)