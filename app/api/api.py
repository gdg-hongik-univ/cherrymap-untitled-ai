from fastapi import APIRouter
from app.api.endpoints import chat, health

# 메인 API 라우터
api_router = APIRouter()

# 하위 라우터들을 메인 라우터에 포함
api_router.include_router(health.router, prefix="", tags=["health"])
api_router.include_router(chat.router, prefix="", tags=["chat"]) 