from ai_resume_writer.contracts.models import CandidateProfile
from ai_resume_writer.rewrite.resume import _validate_rewrite


def validate_generated_resume(
    candidate_profile: CandidateProfile,
    generated_sections: dict[str, list[str]],
) -> dict[str, list[str]]:
    """Validate LLM-generated resume content against candidate evidence.

    The candidate profile is the factual source of truth.
    Generated content may improve wording, but unsupported factual
    content must not bypass the existing resume validation rules.
    """
    original_profile = candidate_profile.model_copy(deep=True)

    validated_sections = _validate_rewrite(
        candidate_profile=original_profile,
        rewrite=generated_sections,
    )

    return validated_sections