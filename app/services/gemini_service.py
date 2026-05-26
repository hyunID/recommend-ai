import json
import logging

from google import genai
from google.genai import types

from app.config import get_gemini_api_key, get_gemini_model

logger = logging.getLogger(__name__)

MAX_KEYWORDS = 10


def _build_prompt(product_name: str, category: str, reviews: list[str]) -> str:
    review_lines = "\n".join(f"- {review}" for review in reviews)
    return f"""다음 상품 정보와 고객 리뷰를 분석해 마케팅·검색에 활용할 추천 키워드를 최대 {MAX_KEYWORDS}개 제안하세요.

상품명: {product_name}
카테고리: {category}
리뷰:
{review_lines}

규칙:
- 리뷰에서 자주 언급되는 장점·특징을 키워드로 추출
- 리뷰와 같은 언어로 작성 (한국어 리뷰면 한국어 키워드)
- 중복 없이 간결한 명사/형용사 위주
- 반드시 아래 JSON 형식만 출력 (다른 텍스트 없음):

{{"recommendKeywords": ["키워드1", "키워드2"]}}"""


def _parse_keywords(text: str) -> list[str] | None:
    try:
        data = json.loads(text.strip())
    except json.JSONDecodeError:
        return None

    keywords = data.get("recommendKeywords")
    if not isinstance(keywords, list):
        return None

    result = [str(k).strip() for k in keywords if str(k).strip()]
    return result[:MAX_KEYWORDS] if result else None


def generate_keywords_with_gemini(
    product_name: str,
    category: str,
    reviews: list[str],
) -> list[str] | None:
    """Gemini API로 추천 키워드를 생성합니다. 실패 시 None을 반환합니다."""
    api_key = get_gemini_api_key()
    if not api_key:
        logger.warning("GEMINI_API_KEY is not set; skipping Gemini API")
        return None

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=get_gemini_model(),
            contents=_build_prompt(product_name, category, reviews),
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.3,
            ),
        )
        text = response.text
        if not text:
            logger.warning("Gemini API returned empty response")
            return None

        keywords = _parse_keywords(text)
        if keywords is None:
            logger.warning("Failed to parse Gemini response: %s", text[:200])
        return keywords

    except Exception as e:
        print(f"Gemini API call failed: {e}")
        return None
