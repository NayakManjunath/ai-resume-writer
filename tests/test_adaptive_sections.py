from ai_resume_writer.contracts.models import CandidateProfile
from ai_resume_writer.documents.sections import select_resume_sections


def test_selects_only_populated_sections():
    profile = CandidateProfile(
        professional_summary="Data Scientist with Python experience.",
        skills=["Python", "SQL"],
        experience=["Data Scientist - Example Company"],
        projects=[],
        education=["B.Tech"],
        certifications=[],
    )

    assert select_resume_sections(profile) == [
        "PROFESSIONAL SUMMARY",
        "SKILLS",
        "EXPERIENCE",
        "EDUCATION",
    ]


def test_selects_all_sections_when_all_are_populated():
    profile = CandidateProfile(
        professional_summary="Data Scientist.",
        skills=["Python"],
        experience=["Data Scientist - Example Company"],
        projects=["Recommendation System"],
        education=["B.Tech"],
        certifications=["AWS Certification"],
    )

    assert select_resume_sections(profile) == [
        "PROFESSIONAL SUMMARY",
        "SKILLS",
        "EXPERIENCE",
        "PROJECTS",
        "EDUCATION",
        "CERTIFICATIONS",
    ]


def test_excludes_empty_lists():
    profile = CandidateProfile(
        skills=[],
        experience=[],
        projects=[],
        education=[],
        certifications=[],
    )

    assert select_resume_sections(profile) == []


def test_excludes_whitespace_only_summary():
    profile = CandidateProfile(
        professional_summary="   ",
    )

    assert select_resume_sections(profile) == []


def test_ignores_empty_items_inside_lists():
    profile = CandidateProfile(
        skills=["", "  ", "Python", ""],
        projects=["", "Recommendation System"],
        education=["  "],
    )

    assert select_resume_sections(profile) == [
        "SKILLS",
        "PROJECTS",
    ]


def test_preserves_defined_section_order():
    profile = CandidateProfile(
        certifications=["AWS Certification"],
        education=["B.Tech"],
        projects=["RAG Project"],
        experience=["Data Scientist"],
        skills=["Python"],
        professional_summary="Data Scientist.",
    )

    assert select_resume_sections(profile) == [
        "PROFESSIONAL SUMMARY",
        "SKILLS",
        "EXPERIENCE",
        "PROJECTS",
        "EDUCATION",
        "CERTIFICATIONS",
    ]


def test_does_not_modify_candidate_profile():
    profile = CandidateProfile(
        professional_summary="Data Scientist.",
        skills=["Python", "SQL"],
        projects=[],
    )

    original_summary = profile.professional_summary
    original_skills = profile.skills.copy()

    select_resume_sections(profile)

    assert profile.professional_summary == original_summary
    assert profile.skills == original_skills