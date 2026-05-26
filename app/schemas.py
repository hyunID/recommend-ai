from typing import Literal

from pydantic import BaseModel, Field

RecommendSource = Literal["gemini", "fallback"]


class RecommendRequest(BaseModel):
    productName: str = Field(..., description="상품명")
    category: str = Field(..., description="카테고리")
    reviews: list[str] = Field(..., description="리뷰 문자열 목록")


class RecommendResponse(BaseModel):
    recommendKeywords: list[str] = Field(..., description="추천 키워드 목록")
    source: RecommendSource = Field(
        ...,
        description="키워드 생성 출처 (gemini: Gemini API, fallback: 로컬 추출)",
    )
