"""
Cherry AI - Google AI Studio LLM Server

FastAPI와 Google AI Studio를 사용한 간단한 LLM 서버입니다.
메시지를 받아서 Google AI Studio에 전달하고 응답을 반환하는 기능을 제공합니다.

주요 기능:
- 💬 Google AI Studio와의 채팅
- 🤖 AI 응답 생성
- 🆓 무료 요금제 지원
- 📊 자동 API 문서 생성
- 🏗️ 모듈화된 구조
"""

import logging
import uvicorn
from fastapi import FastAPI
from app.core.config import settings
from app.api.api import api_router

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """
    FastAPI 애플리케이션 생성
    
    Returns:
        FastAPI: 설정된 FastAPI 애플리케이션 인스턴스
    """
    app = FastAPI(
        title=settings.api_title,
        description=settings.api_description,
        version=settings.api_version,
        contact={
            "name": "Cherry AI",
            "url": "https://github.com/your-repo/cherry-ai",
        },
        license_info={
            "name": "MIT License",
            "url": "https://opensource.org/licenses/MIT",
        },
        tags_metadata=[
            {
                "name": "chat",
                "description": "Google AI Studio와의 채팅 관련 엔드포인트",
            },
            {
                "name": "health",
                "description": "서버 상태 확인 엔드포인트",
            },
        ]
    )
    
    # API 라우터 등록
    app.include_router(api_router)
    
    return app

# FastAPI 앱 인스턴스 생성
app = create_app()

@app.get("/docs")
async def custom_docs():
    """
    ## API 문서
    
    이 서버는 자동으로 생성되는 API 문서를 제공합니다.
    
    ### 사용 가능한 문서
    - **Swagger UI**: `/docs` - 대화형 API 문서
    - **ReDoc**: `/redoc` - 읽기 쉬운 API 문서
    - **OpenAPI Schema**: `/openapi.json` - OpenAPI 스키마
    
    ### 주요 엔드포인트
    - `GET /` - 서버 상태 확인
    - `POST /chat` - Google AI Studio와 채팅
    - `GET /health` - 헬스 체크
    - `GET /info` - 서버 정보
    
    ### 사용 방법
    1. API 문서에서 엔드포인트를 확인하세요
    2. 요청 예시를 참고하여 API를 호출하세요
    3. 응답 형식을 확인하여 데이터를 처리하세요
    """
    return {
        "message": "API 문서에 접근하려면 다음 URL을 사용하세요:",
        "swagger_ui": "/docs",
        "redoc": "/redoc",
        "openapi_schema": "/openapi.json",
        "endpoints": {
            "root": "GET / - 서버 상태 확인",
            "chat": "POST /chat - Google AI Studio와 채팅",
            "health": "GET /health - 헬스 체크",
            "info": "GET /info - 서버 정보"
        }
    }

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행되는 이벤트"""
    logger.info(f"Cherry AI - Google AI Studio LLM Server 시작")
    logger.info(f"서버 주소: http://{settings.host}:{settings.port}")
    logger.info(f"API 문서: http://{settings.host}:{settings.port}/docs")
    logger.info(f"사용 모델: {settings.google_ai_model}")

@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행되는 이벤트"""
    logger.info("Cherry AI - Google AI Studio LLM Server 종료")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level="info"
    ) 