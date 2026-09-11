from enum import Enum

from pydantic import BaseModel, Field


class InformationStatus(str, Enum):
    """Status of information discovered during resume analysis."""

    DETECTED = "detected"
    SUGGESTED = "suggested"
    USER_CONFIRMED = "user_confirmed"


class ResumeFormatChoice(str, Enum):
    """User's decision about the resume format."""

    KEEP_EXISTING = "keep_existing"
    USE_TEMPLATE = "use_template"


class ResumeDocument(BaseModel):
    """Structured representation of an uploaded resume."""

    file_name: str = Field(min_length=1)
    file_type: str = Field(min_length=1)
    raw_text: str = Field(min_length=1)
    sections: list[str] = Field(default_factory=list)


class JobDescription(BaseModel):
    """Structured representation of a job description."""

    raw_text: str
    title: str | None = None
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)


class CandidateProfile(BaseModel):
    """Candidate information extracted from the resume."""

    name: str | None = None
    professional_summary: str | None = None
    skills: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    experience_years: float | None = None
    education: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)


class TargetRole(BaseModel):
    """Resolved target designation for resume tailoring."""

    designation: str
    source: str


class GapItem(BaseModel):
    """Potential resume/JD gap requiring user review."""

    category: str
    item: str
    reason: str
    status: InformationStatus = InformationStatus.DETECTED


class UserConfirmation(BaseModel):
    """User decision regarding a suggested piece of information."""

    gap_item: str
    confirmed: bool
    additional_information: str | None = None


class ResumeAnalysis(BaseModel):
    """Combined analysis of resume and target job description."""

    target_role: TargetRole
    candidate_profile: CandidateProfile
    gaps: list[GapItem] = Field(default_factory=list)


class ResumeImprovement(BaseModel):
    """Result of the resume improvement process."""

    target_role: TargetRole
    format_choice: ResumeFormatChoice
    original_profile: CandidateProfile
    improved_sections: dict[str, list[str]] = Field(default_factory=dict)
    improvement_summary: list[str] = Field(default_factory=list)