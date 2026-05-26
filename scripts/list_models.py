"""임시 스크립트: Gemini 사용 가능 모델 목록 조회.

프로젝트 루트에서 실행:
    python scripts/list_models.py
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from google import genai

from app.config import get_gemini_api_key, load_env


def main() -> None:
    load_env()
    api_key = get_gemini_api_key()
    if not api_key:
        print("ERROR: GEMINI_API_KEY is not set in .env")
        sys.exit(1)

    client = genai.Client(api_key=api_key)
    models = list(client.models.list())

    if not models:
        print("No models returned.")
        return

    print(f"Found {len(models)} model(s):\n")
    for model in sorted(models, key=lambda m: m.name or ""):
        name = model.name or "(unknown)"
        display = model.display_name or ""
        actions = model.supported_actions or []

        print(f"- name: {name}")
        if display:
            print(f"  display_name: {display}")
        if actions:
            print(f"  supported_actions: {', '.join(actions)}")
        else:
            print("  supported_actions: (none)")
        print()


if __name__ == "__main__":
    main()
