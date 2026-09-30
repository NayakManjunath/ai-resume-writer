import json

from ai_resume_writer.ai.client import create_groq_client
from ai_resume_writer.contracts.models import (
    CandidateProfile,
    JobDescription,
    ResumeFormatChoice,
    ResumeImprovement,
    TargetRole,
)
from ai_resume_writer.alignment.matcher import (
    ResumeJDAlignment,
    align_resume_with_job_description,
)
from ai_resume_writer.rewrite.resume import (
    _build_rewrite_schema,
    _contains_unsupported_metric,
    _source_values,
    _validate_section_values,
    GROQ_MODEL,
    _ALLOWED_SECTIONS,
)


def _build_tailoring_payload(
    candidate_profile: CandidateProfile,
    job_description: JobDescription,
    target_role: TargetRole,
    alignment: ResumeJDAlignment,
) -> str:
    """Build the factual candidate and JD evidence sent to the LLM."""
    return json.dumps(
        {
            "target_role": target_role.model_dump(),
            "candidate_profile": candidate_profile.model_dump(),
            "job_description": job_description.model_dump(),
            "alignment": {
                "matched_required_skills": alignment.matched_required_skills,
                "matched_preferred_skills": alignment.matched_preferred_skills,
                "resume_only_skills": alignment.resume_only_skills,
                "candidate_projects": alignment.candidate_projects,
                "candidate_experience": alignment.candidate_experience,
            },
        },
        ensure_ascii=False,
    )


def _generate_tailored_rewrite(
    candidate_profile: CandidateProfile,
    job_description: JobDescription,
    target_role: TargetRole,
    alignment: ResumeJDAlignment,
) -> dict[str, list[str]]:
    """Generate a JD-tailored rewrite using only candidate evidence."""
    client = create_groq_client()

    system_prompt = """
You are a professional resume tailoring assistant.

Tailor the candidate's existing resume content toward the supplied
Job Description.

The Job Description is a relevance signal only.
The candidate profile is the factual source of truth.

STRICT FACTUAL RULES:

- Use only information present in the candidate profile.
- Use the Job Description only to prioritize relevant existing evidence.
- Do not add skills that are not present in the candidate profile.
- Do not add projects that are not present in the candidate profile.
- Do not add employers.
- Do not add education.
- Do not add certifications.
- Do not invent achievements.
- Do not invent numbers, percentages, metrics, dates, users,
  performance results, accuracy, revenue, time savings, or scale.
- Do not convert a Job Description requirement into candidate experience.
- Do not claim that the candidate possesses a missing JD skill.
- You may improve wording and ordering of existing evidence.
- You may emphasize candidate evidence that is relevant to the JD.
- If a section has no candidate information, return an empty list.
- Return only the requested JSON structure.
"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": _build_tailoring_payload(
                    candidate_profile,
                    job_description,
                    target_role,
                    alignment,
                ),
            },
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "resume_jd_tailoring",
                "strict": True,
                "schema": _build_rewrite_schema(),
            },
        },
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError(
            "Groq returned an empty JD tailoring response."
        )

    result = json.loads(content)

    if not isinstance(result, dict):
        raise ValueError(
            "Groq JD tailoring response must be a JSON object."
        )

    return result


def _validate_tailored_rewrite(
    candidate_profile: CandidateProfile,
    rewrite: dict[str, list[str]],
) -> dict[str, list[str]]:
    """
    Apply the same factual safety boundary used by 5.1.

    JD tailoring may change emphasis, but it cannot bypass the
    candidate-evidence validation rules.
    """
    if not isinstance(rewrite, dict):
        raise ValueError("Tailored rewrite must be a dictionary.")

    validated: dict[str, list[str]] = {}

    for section, values in rewrite.items():
        if section not in _ALLOWED_SECTIONS:
            continue

        if not isinstance(values, list):
            raise ValueError(
                f"Tailored rewrite section '{section}' must contain a list."
            )

        original_items = _source_values(
            candidate_profile,
            section,
        )

        if not original_items:
            if values:
                validated[section] = []
            continue

        cleaned_values = _validate_section_values(
            section=section,
            original_items=original_items,
            values=values,
        )

        validated[section] = cleaned_values

    return validated


def tailor_resume(
    candidate_profile: CandidateProfile,
    job_description: JobDescription,
    target_role: TargetRole,
) -> ResumeImprovement:
    """Tailor existing resume evidence toward a supplied Job Description."""
    original_profile = candidate_profile.model_copy(deep=True)

    alignment = align_resume_with_job_description(
        candidate_profile=candidate_profile,
        job_description=job_description,
        target_role=target_role,
    )

    rewrite = _generate_tailored_rewrite(
        candidate_profile,
        job_description,
        target_role,
        alignment,
    )

    validated_sections = _validate_tailored_rewrite(
        candidate_profile,
        rewrite,
    )

    return ResumeImprovement(
        target_role=target_role,
        format_choice=ResumeFormatChoice.KEEP_EXISTING,
        original_profile=original_profile,
        improved_sections=validated_sections,
        improvement_summary=[],
    )