from openai import OpenAI
import pytest

from ai_resume_writer.ai.client import create_groq_client
from ai_resume_writer.config.settings import get_groq_api_key


def test_missing_groq_api_key_raises_error(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="GROQ_API_KEY"):
        get_groq_api_key()


def test_groq_api_key_is_loaded_from_environment(monkeypatch):
    monkeypatch.setenv(
        "GROQ_API_KEY",
        "test-key",
    )

    assert get_groq_api_key() == "test-key"


def test_create_groq_client_uses_configured_key(monkeypatch):
    monkeypatch.setenv(
        "GROQ_API_KEY",
        "test-key",
    )

    client = create_groq_client()

    assert isinstance(client, OpenAI)