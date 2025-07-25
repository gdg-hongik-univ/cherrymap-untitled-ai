"""
API 라우터 설정

이 모듈은 Cherry AI LLM Server의 모든 API 엔드포인트를 통합합니다.
"""

from fastapi import APIRouter
from app.api.endpoints import chat, health

# 메인 API 라우터
api_router = APIRouter()

# 엔드포인트 등록
api_router.include_router(chat.router, prefix="/api/v1")
api_router.include_router(health.router, prefix="/api/v1") 