import os
from pathlib import Path

from dotenv import load_dotenv

# app/config.py → 프로젝트 루트(recommend-ai)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"


def load_env() -> bool:
    """프로젝트 루트의 .env 파일을 로드합니다."""
    return load_dotenv(dotenv_path=ENV_FILE)


def get_gemini_api_key() -> str | None:
    value = os.getenv("GEMINI_API_KEY")
    if value is None:
        return None
    value = value.strip()
    return value or None


DEFAULT_GEMINI_MODEL = "gemini-1.5-flash"


def get_gemini_model() -> str:
    return os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL).strip() or DEFAULT_GEMINI_MODEL
