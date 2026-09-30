import os

from dotenv import load_dotenv


load_dotenv()


def get_groq_api_key() -> str:
    """Return the configured Groq API key."""
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not configured."
        )

    return api_key