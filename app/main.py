import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import load_env
from app.schemas import RecommendRequest, RecommendResponse
from app.services.recommend_service import generate_recommend_keywords

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(_: FastAPI):
    loaded = load_env()
    if loaded:
        logging.info("Loaded environment from .env")
    else:
        logging.warning(".env file not found or empty; using system environment only")
    yield


app = FastAPI(
    title="AI Recommend Server",
    description="상품 리뷰 기반 추천 키워드 API",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/recommend", response_model=RecommendResponse)
def recommend(request: RecommendRequest) -> RecommendResponse:
    keywords, source = generate_recommend_keywords(
        product_name=request.productName,
        category=request.category,
        reviews=request.reviews,
    )
    return RecommendResponse(recommendKeywords=keywords, source=source)
