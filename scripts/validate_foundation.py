from pathlib import Path
import importlib
import sys

from pydantic import ValidationError

from ai_resume_writer.contracts.models import (
    CandidateProfile,
    GapItem,
    InformationStatus,
    JobDescription,
    ResumeAnalysis,
    ResumeDocument,
    ResumeFormatChoice,
    ResumeImprovement,
    TargetRole,
    UserConfirmation,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def validate_python_environment() -> None:
    """Validate the Python version used by the project."""

    major, minor = sys.version_info[:2]

    if (major, minor) < (3, 11) or (major, minor) >= (3, 13):
        raise AssertionError(
            f"Unsupported Python version: {major}.{minor}"
        )


def validate_project_structure() -> None:
    """Validate required foundation directories and files."""

    required_paths = [
        ".env.example",
        ".gitignore",
        "README.md",
        "pyproject.toml",
        "src",
        "src/ai_resume_writer",
        "src/ai_resume_writer/config",
        "src/ai_resume_writer/contracts",
        "src/ai_resume_writer/resume",
        "src/ai_resume_writer/jd",
        "src/ai_resume_writer/ai",
        "src/ai_resume_writer/documents",
        "src/ai_resume_writer/ui",
        "tests",
    ]

    missing_paths = [
        path
        for path in required_paths
        if not (PROJECT_ROOT / path).exists()
    ]

    if missing_paths:
        raise AssertionError(
            f"Missing project paths: {', '.join(missing_paths)}"
        )


def validate_dependencies() -> None:
    """Validate that required project packages can be imported."""

    packages = [
        "openai",
        "pydantic",
        "dotenv",
        "streamlit",
        "docx",
        "pypdf",
        "reportlab",
        "pytest",
    ]

    failed = []

    for package in packages:
        try:
            importlib.import_module(package)
        except ImportError:
            failed.append(package)

    if failed:
        raise AssertionError(
            f"Failed dependency imports: {', '.join(failed)}"
        )


def validate_configuration_protection() -> None:
    """Validate that .env is ignored by Git."""

    gitignore_path = PROJECT_ROOT / ".gitignore"

    if not gitignore_path.exists():
        raise AssertionError(".gitignore does not exist.")

    gitignore_content = gitignore_path.read_text(
        encoding="utf-8"
    )

    if ".env" not in gitignore_content:
        raise AssertionError(
            ".env is not protected by .gitignore."
        )


def validate_data_contracts() -> None:
    """Validate the core Pydantic data contracts."""

    resume = ResumeDocument(
        file_name="sample.pdf",
        file_type="pdf",
        raw_text="Sample resume text",
    )

    jd = JobDescription(
        raw_text="Looking for a Data Scientist with Python and SQL."
    )

    profile = CandidateProfile(
        name="Test Candidate",
        skills=["Python", "Pandas"],
    )

    role = TargetRole(
        designation="Data Scientist",
        source="job_description",
    )

    gap = GapItem(
        category="skill",
        item="SQL",
        reason="SQL was not found in the resume.",
    )

    confirmation = UserConfirmation(
        gap_item="SQL",
        confirmed=True,
        additional_information="Used SQL for data analysis.",
    )

    analysis = ResumeAnalysis(
        target_role=role,
        candidate_profile=profile,
        gaps=[gap],
    )

    improvement = ResumeImprovement(
        target_role=role,
        format_choice=ResumeFormatChoice.KEEP_EXISTING,
        original_profile=profile,
        improved_sections={
            "skills": ["Python", "Pandas"]
        },
        improvement_summary=[
            "Improved resume alignment."
        ],
    )

    assert resume.file_name == "sample.pdf"
    assert jd.raw_text
    assert profile.name == "Test Candidate"
    assert role.designation == "Data Scientist"
    assert gap.status == InformationStatus.DETECTED
    assert confirmation.confirmed is True
    assert len(analysis.gaps) == 1
    assert (
        improvement.format_choice
        == ResumeFormatChoice.KEEP_EXISTING
    )


def validate_invalid_contract_rejection() -> None:
    """Verify that invalid contract data is rejected."""

    try:
        ResumeDocument(
            file_name="",
            file_type="pdf",
            raw_text="Sample resume text",
        )
    except ValidationError:
        return

    raise AssertionError(
        "Invalid ResumeDocument was not rejected."
    )


def main() -> None:
    print("Starting AI Resume Writer foundation validation...\n")

    validations = [
        (
            "Python environment",
            validate_python_environment,
        ),
        (
            "Project structure",
            validate_project_structure,
        ),
        (
            "Dependencies",
            validate_dependencies,
        ),
        (
            "Configuration protection",
            validate_configuration_protection,
        ),
        (
            "Core data contracts",
            validate_data_contracts,
        ),
        (
            "Invalid contract rejection",
            validate_invalid_contract_rejection,
        ),
    ]

    for name, validator in validations:
        validator()
        print(f"{name}: PASSED")

    print("\nFoundation Validation: PASSED")


if __name__ == "__main__":
    main()