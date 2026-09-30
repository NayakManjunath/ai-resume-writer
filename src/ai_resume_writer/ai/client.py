from openai import OpenAI

from ai_resume_writer.config.settings import get_groq_api_key


GROQ_BASE_URL = "https://api.groq.com/openai/v1"


def create_groq_client() -> OpenAI:
    """Create an OpenAI-compatible client configured for Groq."""
    return OpenAI(
        api_key=get_groq_api_key(),
        base_url=GROQ_BASE_URL,
    )