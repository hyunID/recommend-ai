import re
from collections import Counter

from app.schemas import RecommendSource
from app.services.gemini_service import generate_keywords_with_gemini

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of",
    "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "do", "does", "did", "will", "would", "could", "should", "may", "might",
    "must", "shall", "can", "need", "dare", "ought", "used", "it", "its",
    "this", "that", "these", "those", "i", "you", "he", "she", "we", "they",
    "what", "which", "who", "whom", "whose", "where", "when", "why", "how",
    "all", "each", "every", "both", "few", "more", "most", "other", "some",
    "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too",
    "very", "just", "also", "now", "here", "there", "then", "once",
    "이", "그", "저", "것", "수", "등", "및", "또", "더", "좀", "잘", "안",
    "있", "없", "하", "되", "된", "되는", "한", "할", "함", "합", "다",
    "습니다", "입니다", "있습니다", "없습니다", "해요", "이에요", "예요",
    "정말", "너무", "진짜", "그냥", "약간", "조금", "매우", "아주",
}

MAX_KEYWORDS = 10


def _tokenize(text: str) -> list[str]:
    text = text.lower()
    tokens = re.findall(r"[a-zA-Z]{2,}|[가-힣]{2,}", text)
    return [t for t in tokens if t not in STOPWORDS and len(t) >= 2]


def extract_keywords_fallback(
    product_name: str,
    category: str,
    reviews: list[str],
) -> list[str]:
    """리뷰·상품명·카테고리에서 빈도 기반 추천 키워드를 추출합니다."""
    texts = [product_name, category, *reviews]
    combined = " ".join(texts)
    tokens = _tokenize(combined)

    if not tokens:
        base = _tokenize(f"{product_name} {category}")
        return base[:MAX_KEYWORDS] if base else [category.strip(), product_name.strip()][:MAX_KEYWORDS]

    freq = Counter(tokens)
    ranked = [word for word, _ in freq.most_common(MAX_KEYWORDS * 2)]

    seen: set[str] = set()
    keywords: list[str] = []

    for word in ranked:
        if word not in seen:
            seen.add(word)
            keywords.append(word)
        if len(keywords) >= MAX_KEYWORDS:
            break

    category_tokens = _tokenize(category)
    for token in category_tokens:
        if token not in seen and len(keywords) < MAX_KEYWORDS:
            seen.add(token)
            keywords.insert(0, token)

    return keywords[:MAX_KEYWORDS]


def generate_recommend_keywords(
    product_name: str,
    category: str,
    reviews: list[str],
) -> tuple[list[str], RecommendSource]:
    """Gemini API로 키워드를 생성하고, 실패 시 로컬 추출 로직으로 대체합니다."""
    keywords = generate_keywords_with_gemini(product_name, category, reviews)
    if keywords:
        return keywords, "gemini"
    return extract_keywords_fallback(product_name, category, reviews), "fallback"
