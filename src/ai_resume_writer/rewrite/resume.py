import json
import re

from ai_resume_writer.ai.client import create_groq_client
from ai_resume_writer.contracts.models import (
    CandidateProfile,
    ResumeFormatChoice,
    ResumeImprovement,
    TargetRole,
)

GROQ_MODEL = "openai/gpt-oss-20b"

_ALLOWED_SECTIONS = {
    "professional_summary",
    "skills",
    "experience",
    "projects",
    "education",
    "certifications",
}

_SECTION_SOURCE_FIELDS = {
    "professional_summary": "professional_summary",
    "skills": "skills",
    "experience": "experience",
    "projects": "projects",
    "education": "education",
    "certifications": "certifications",
}

# Metric expressions that can represent factual claims.
# The percent pattern intentionally does not use a word boundary
# after "%" because "%" is not a word character.
_METRIC_PATTERN = re.compile(
    r"\b\d+(?:\.\d+)?\s*%"
    r"|\b\d+(?:\.\d+)?\s+percent\b"
    r"|\b\d+(?:\.\d+)?\s*(?:x|times)\b"
    r"|\b\d+(?:\.\d+)?\s+"
    r"(?:users?|documents?|records?|requests?|transactions?|projects?|"
    r"months?|years?|hours?|minutes?|seconds?)\b",
    re.IGNORECASE,
)


def _build_rewrite_schema() -> dict:
    """Return the strict JSON schema expected from Groq."""
    section_item = {
        "type": "array",
        "items": {"type": "string"},
    }

    return {
        "type": "object",
        "properties": {
            "professional_summary": section_item,
            "skills": section_item,
            "experience": section_item,
            "projects": section_item,
            "education": section_item,
            "certifications": section_item,
        },
        "required": [
            "professional_summary",
            "skills",
            "experience",
            "projects",
            "education",
            "certifications",
        ],
        "additionalProperties": False,
    }


def _build_rewrite_payload(
    candidate_profile: CandidateProfile,
    target_role: TargetRole,
) -> str:
    """Build the factual candidate input sent to the LLM."""
    return json.dumps(
        {
            "target_role": target_role.model_dump(),
            "candidate_profile": candidate_profile.model_dump(),
        },
        ensure_ascii=False,
    )


def _generate_rewrite(
    candidate_profile: CandidateProfile,
    target_role: TargetRole,
) -> dict[str, list[str]]:
    """Generate a structured rewrite proposal using Groq."""
    client = create_groq_client()

    system_prompt = """
You are a professional resume rewriting assistant.

Rewrite the candidate's existing resume content for clarity,
professional wording, and stronger presentation.

STRICT FACTUAL RULES:

- Use only information present in the candidate profile.
- Do not add skills.
- Do not add projects.
- Do not add employers.
- Do not add education.
- Do not add certifications.
- Do not invent achievements.
- Do not invent numbers, percentages, metrics, dates, users,
  performance results, accuracy, revenue, time savings, or scale.
- Do not create information merely because it is useful for the
  target role.
- You may improve wording without changing the underlying fact.
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
                "content": _build_rewrite_payload(
                    candidate_profile,
                    target_role,
                ),
            },
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "resume_rewrite",
                "strict": True,
                "schema": _build_rewrite_schema(),
            },
        },
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("Groq returned an empty rewrite response.")

    result = json.loads(content)

    if not isinstance(result, dict):
        raise ValueError("Groq rewrite response must be a JSON object.")

    return result


def _source_values(
    candidate_profile: CandidateProfile,
    section: str,
) -> list[str]:
    """Return the original candidate evidence for a section."""
    field_name = _SECTION_SOURCE_FIELDS[section]
    value = getattr(candidate_profile, field_name)

    if isinstance(value, list):
        return [
            item.strip()
            for item in value
            if isinstance(item, str) and item.strip()
        ]

    if isinstance(value, str) and value.strip():
        return [value.strip()]

    return []


def _normalize_text(value: str) -> str:
    """Normalize text for deterministic comparison."""
    return " ".join(value.strip().lower().split())


def _extract_metrics(text: str) -> set[str]:
    """Extract factual metric expressions from text."""
    return {
        match.group(0).strip().lower()
        for match in _METRIC_PATTERN.finditer(text)
    }


def _contains_unsupported_metric(
    original_items: list[str],
    rewritten_item: str,
) -> bool:
    """Return True when a rewrite introduces a new metric."""
    original_metrics = {
        metric
        for item in original_items
        for metric in _extract_metrics(item)
    }

    rewritten_metrics = _extract_metrics(rewritten_item)

    return not rewritten_metrics.issubset(original_metrics)


def _validate_skills(
    original_items: list[str],
    rewritten_values: list[str],
) -> list[str]:
    """
    Keep only skills that already exist in the candidate profile.

    The LLM may improve presentation, but it cannot introduce a
    previously unsupported skill.
    """
    original_skills = {
        _normalize_text(skill)
        for skill in original_items
    }

    validated: list[str] = []
    seen: set[str] = set()

    for value in rewritten_values:
        if not isinstance(value, str):
            raise ValueError("Rewrite item in 'skills' must be a string.")

        skill = value.strip()

        if not skill:
            continue

        normalized_skill = _normalize_text(skill)

        if normalized_skill not in original_skills:
            continue

        if normalized_skill in seen:
            continue

        seen.add(normalized_skill)
        validated.append(skill)

    return validated


def _validate_section_values(
    section: str,
    original_items: list[str],
    values: list[str],
) -> list[str]:
    """
    Validate rewritten values against the original candidate evidence.

    This is intentionally conservative:
    - unsupported sections are ignored
    - unsupported skills are removed
    - unsupported metrics cause the complete rewritten item to be rejected
    - empty rewritten items are removed
    """
    if section == "skills":
        return _validate_skills(
            original_items,
            values,
        )

    cleaned_values: list[str] = []

    for value in values:
        if not isinstance(value, str):
            raise ValueError(
                f"Rewrite item in '{section}' must be a string."
            )

        rewritten_item = value.strip()

        if not rewritten_item:
            continue

        # A newly introduced metric is a factual claim.
        # Reject the complete bullet instead of deleting only the number,
        # which could leave misleading or grammatically invalid content.
        if _contains_unsupported_metric(
            original_items,
            rewritten_item,
        ):
            continue

        cleaned_values.append(rewritten_item)

    return cleaned_values


def _validate_rewrite(
    candidate_profile: CandidateProfile,
    rewrite: dict[str, list[str]],
) -> dict[str, list[str]]:
    """Keep only sections and content supported by candidate evidence."""
    if not isinstance(rewrite, dict):
        raise ValueError("Rewrite must be a dictionary.")

    validated: dict[str, list[str]] = {}

    for section, values in rewrite.items():
        if section not in _ALLOWED_SECTIONS:
            continue

        if not isinstance(values, list):
            raise ValueError(
                f"Rewrite section '{section}' must contain a list."
            )

        original_items = _source_values(
            candidate_profile,
            section,
        )

        # If the candidate has no source evidence for this section,
        # preserve the section as empty only when the LLM explicitly
        # attempted to return that section.
        if not original_items:
            if values:
                validated[section] = []
            continue

        cleaned_values = _validate_section_values(
            section=section,
            original_items=original_items,
            values=values,
        )

        # Preserve the section when the candidate has source evidence,
        # even if every proposed rewrite item was rejected.
        validated[section] = cleaned_values

    return validated

def rewrite_resume(
    candidate_profile: CandidateProfile,
    target_role: TargetRole,
) -> ResumeImprovement:
    """Rewrite existing candidate information without fabricating facts."""
    original_profile = candidate_profile.model_copy(deep=True)

    rewrite = _generate_rewrite(
        candidate_profile,
        target_role,
    )

    validated_sections = _validate_rewrite(
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