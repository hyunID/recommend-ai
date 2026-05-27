# AI Recommend Server

FastAPI 기반 상품 리뷰 추천 키워드 API 서버입니다.  
Gemini API로 키워드를 생성하며, API 호출 실패 시 로컬 빈도 기반 추출로 자동 대체(fallback)합니다.

## 요구 사항

- Python 3.10 이상
- [Google AI Studio](https://aistudio.google.com/) Gemini API 키

## 설치

```bash
cd recommend-ai
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## Gemini API 설정

1. [Google AI Studio](https://aistudio.google.com/apikey)에서 API 키를 발급합니다.
2. 프로젝트 루트에 환경 변수 파일을 만듭니다.

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

3. `.env` 파일에 발급받은 키를 설정합니다.

```env
GEMINI_API_KEY=your_actual_api_key_here
```

| 변수 | 필수 | 설명 |
|------|------|------|
| `GEMINI_API_KEY` | 권장 | Gemini API 키. 미설정 시 fallback만 사용 |
| `GEMINI_MODEL` | 선택 | 사용 모델 (기본값: `gemini-1.5-flash`, 예: `gemini-1.5-flash-latest`) |

> `.env`는 Git에 포함되지 않습니다. 팀원에게는 `.env.example`만 공유하세요.

## 실행

### 로컬 (Python)

프로젝트 루트(`recommend-ai`)에서 실행합니다.

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker

`.env`는 이미지에 포함하지 않습니다. 빌드 후 실행 시 `--env-file`로 전달합니다.

```bash
# 이미지 빌드
docker build -t recommend-ai .

# 컨테이너 실행 (로컬 8000 포트)
docker run --rm -p 8000:8000 --env-file .env recommend-ai
```

`.env`가 없다면 `.env.example`을 복사해 키를 설정한 뒤 실행하세요.

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

백그라운드 실행 예시:

```bash
docker run -d --name recommend-ai -p 8000:8000 --env-file .env recommend-ai
```

- API 문서(Swagger): http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- 헬스체크: http://localhost:8000/health

### Render 배포

운영 환경(Render Web Service) 기준 설정 예시입니다.

| 항목 | 값 |
|------|-----|
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Health Check | `/health` |

Render Environment Variables:

| 변수 | 필수 | 설명 |
|------|------|------|
| `GEMINI_API_KEY` | ✅ | Gemini API 키 |
| `GEMINI_MODEL` | 선택 | 기본값 `gemini-1.5-flash` |

운영 URL 예시: `https://recommend-ai-o88u.onrender.com`

> `.env` 파일은 Render 대시보드의 Environment Variables로 설정합니다. 저장소에 커밋하지 마세요.

`commerce-api` 연동 시 prod profile의 `recommend-ai.base-url`을 위 운영 URL로 설정합니다.

## API

### `POST /recommend`

상품명, 카테고리, 리뷰 목록을 받아 추천 키워드를 반환합니다.

**요청 예시**

```json
{
  "productName": "무선 블루투스 이어폰",
  "category": "전자기기",
  "reviews": [
    "음질이 선명하고 배터리가 오래가요",
    "착용감이 편하고 노이즈 캔슬링이 좋아요",
    "가격 대비 음질이 훌륭합니다"
  ]
}
```

**응답 예시**

```json
{
  "recommendKeywords": [
    "음질",
    "배터리",
    "착용감",
    "노이즈 캔슬링",
    "가성비",
    "블루투스",
    "무선",
    "이어폰",
    "전자기기",
    "편안함"
  ],
  "source": "gemini"
}
```

| `source` | 설명 |
|----------|------|
| `gemini` | Gemini API로 키워드 생성 성공 |
| `fallback` | Gemini 실패 또는 API 키 미설정 시 로컬 추출 사용 |

### cURL 예시

```bash
curl -X POST "http://localhost:8000/recommend" \
  -H "Content-Type: application/json" \
  -d "{\"productName\":\"무선 블루투스 이어폰\",\"category\":\"전자기기\",\"reviews\":[\"음질이 선명하고 배터리가 오래가요\",\"착용감이 편합니다\"]}"
```

## 동작 방식

1. `GEMINI_API_KEY`가 있으면 Gemini API로 리뷰 기반 키워드를 생성합니다.
2. API 키가 없거나, 네트워크·응답 파싱 오류 등으로 실패하면 기존 빈도 기반 로컬 추출 로직으로 fallback 합니다.
3. 응답의 `source` 필드로 생성 출처(`gemini` / `fallback`)를 확인할 수 있습니다.

## 유틸리티

Gemini 사용 가능 모델 목록 확인:

```bash
python scripts/list_models.py
```

`.env`의 `GEMINI_API_KEY`를 사용하며, 모델명과 `supported_actions`를 출력합니다.

## 프로젝트 구조

```
recommend-ai/
├── app/
│   ├── config.py                 # .env 로드 및 설정
│   ├── main.py                   # FastAPI 앱 및 라우트
│   ├── schemas.py                # 요청/응답 모델
│   └── services/
│       ├── gemini_service.py     # Gemini API 연동
│       └── recommend_service.py  # 키워드 생성 (Gemini + fallback)
├── scripts/
│   └── list_models.py            # Gemini 모델 목록 조회 (임시)
├── .env.example
├── .dockerignore
├── .gitignore
├── Dockerfile
├── requirements.txt
└── README.md
```
