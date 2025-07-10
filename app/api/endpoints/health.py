"""
헬스 체크 API 엔드포인트

이 모듈은 서버 상태 확인을 위한 API 엔드포인트를 정의합니다.
서버 상태, 헬스 체크, 서버 정보 등의 기능을 제공합니다.
"""

import logging
from fastapi import APIRouter
from app.models.schemas import ServerStatus, HealthStatus
from app.core.config import settings
from app.services.google_ai_service import google_ai_service

# 로거 설정
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=ServerStatus, tags=["health"])
async def root():
    """
    ## 서버 상태 확인
    
    서버가 정상적으로 실행 중인지 확인하는 엔드포인트입니다.
    
    ### 응답
    - **message**: 서버 상태 메시지
    - **model**: 사용 중인 AI 모델
    - **status**: 서버 상태 (active/inactive)
    
    ### 응답 예시
    ```json
    {
        "message": "Cherry AI - Google AI Studio LLM Server is running!",
        "model": "gemini-pro",
        "status": "active"
    }
    ```
    """
    logger.debug("서버 상태 확인 요청")
    
    return ServerStatus(
        message="Cherry AI - Google AI Studio LLM Server is running!",
        model=settings.google_ai_model,
        status="active"
    )

@router.get("/health", response_model=HealthStatus, tags=["health"])
async def health_check():
    """
    ## 헬스 체크
    
    서버의 헬스 상태를 확인하는 엔드포인트입니다.
    Google AI Studio 서비스의 연결 상태도 함께 확인합니다.
    
    ### 응답
    - **status**: 서버 헬스 상태 (healthy/unhealthy)
    - **model**: 사용 중인 AI 모델
    
    ### 응답 예시
    ```json
    {
        "status": "healthy",
        "model": "gemini-pro"
    }
    ```
    
    ### 상태 설명
    - `healthy`: 서버와 Google AI Studio 서비스가 모두 정상
    - `unhealthy`: 서버는 정상이지만 Google AI Studio 서비스에 문제
    """
    logger.debug("헬스 체크 요청")
    
    try:
        # Google AI Studio 서비스 헬스 체크
        google_ai_healthy = await google_ai_service.health_check()
        
        status_value = "healthy" if google_ai_healthy else "unhealthy"
        
        logger.info(f"헬스 체크 완료. 상태: {status_value}")
        
        return HealthStatus(
            status=status_value,
            model=settings.google_ai_model
        )
        
    except Exception as e:
        logger.error(f"헬스 체크 중 오류 발생: {str(e)}")
        
        return HealthStatus(
            status="unhealthy",
            model=settings.google_ai_model
        )

@router.get("/info", tags=["health"])
async def get_server_info():
    """
    ## 서버 정보
    
    서버와 모델의 상세 정보를 반환하는 엔드포인트입니다.
    
    ### 응답
    - **server**: 서버 정보 (제목, 버전, 호스트, 포트)
    - **model**: 모델 정보 (모델명, 기본 설정, 지원 모델)
    
    ### 응답 예시
    ```json
    {
        "server": {
            "title": "Cherry AI - Google AI Studio LLM Server",
            "version": "1.0.0",
            "host": "0.0.0.0",
            "port": 8000
        },
        "model": {
            "model": "gemini-pro",
            "temperature_default": 0.7,
            "max_tokens_default": 1000,
            "supported_models": [
                "gemini-pro",
                "gemini-pro-vision",
                "gemini-1.5-pro",
                "gemini-1.5-flash"
            ]
        }
    }
    ```
    """
    logger.debug("서버 정보 요청")
    
    return {
        "server": {
            "title": settings.api_title,
            "version": settings.api_version,
            "host": settings.host,
            "port": settings.port
        },
        "model": google_ai_service.get_model_info()
    } 