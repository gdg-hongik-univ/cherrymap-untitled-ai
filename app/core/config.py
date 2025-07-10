"""
애플리케이션 설정 관리 모듈

이 모듈은 Cherry AI LLM Server의 모든 설정을 중앙에서 관리합니다.
환경 변수, API 설정, 서버 설정 등을 포함합니다.
"""

import os
from typing import Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

class Settings(BaseSettings):
    """
    애플리케이션 설정 클래스
    
    모든 설정값은 환경 변수나 .env 파일에서 로드됩니다.
    기본값이 설정되어 있어 개발 환경에서 바로 사용 가능합니다.
    """
    
    # ==================== API 설정 ====================
    api_title: str = Field(
        default="Cherry AI - Google AI Studio LLM Server", 
        description="API 제목"
    )
    api_version: str = Field(
        default="1.0.0", 
        description="API 버전"
    )
    api_description: str = Field(
        default="""
        ## Cherry AI - Google AI Studio LLM Server
        
        FastAPI와 Google AI Studio를 사용한 간단한 LLM 서버입니다.
        
        ### 주요 기능
        - 💬 메시지를 받아서 Google AI Studio에 전달
        - 🤖 Google AI Studio의 응답을 클라이언트에 반환
        - 🆓 무료 요금제 지원 (gemini-pro 모델)
        - 📊 실시간 API 문서 제공
        - 🏗️ 모듈화된 구조로 확장 가능
        
        ### 사용 방법
        1. Google AI Studio에서 API 키를 발급받으세요
        2. `.env` 파일에 `GOOGLE_API_KEY=your_api_key`를 설정하세요
        3. 서버를 실행하고 `/chat` 엔드포인트로 요청을 보내세요
        
        ### 무료 요금제 제한사항
        - Gemini Pro 모델 사용
        - 분당 요청 수 제한
        - 월간 사용량 제한
        
        자세한 제한사항은 [Google AI Studio](https://aistudio.google.com/)에서 확인하세요.
        """,
        description="API 설명"
    )
    
    # ==================== 서버 설정 ====================
    host: str = Field(
        default="0.0.0.0", 
        description="서버 호스트 주소"
    )
    port: int = Field(
        default=8000, 
        description="서버 포트 번호",
        ge=1024,
        le=65535
    )
    reload: bool = Field(
        default=True, 
        description="개발 모드에서 자동 리로드 여부"
    )
    
    # ==================== Google AI 설정 ====================
    google_api_key: str = Field(
        ..., 
        description="Google AI Studio API 키 (필수)"
    )
    google_ai_model: str = Field(
        default="gemini-1.5-flash", 
        description="사용할 Google AI Studio 모델명"
    )
    
    # ==================== 생성 설정 ====================
    default_temperature: float = Field(
        default=0.7, 
        description="기본 temperature 값 (0.0 ~ 1.0)",
        ge=0.0,
        le=1.0
    )
    default_max_tokens: int = Field(
        default=1000, 
        description="기본 최대 토큰 수",
        ge=1,
        le=8000
    )
    
    # ==================== 검증 메서드 ====================
    @validator('google_ai_model')
    def validate_google_ai_model(cls, v):
        """Google AI 모델명 검증"""
        valid_models = [
            'gemini-1.5-flash',
            'gemini-1.5-pro',
            'gemini-pro',
            'gemini-pro-vision'
        ]
        if v not in valid_models:
            raise ValueError(f'지원하지 않는 모델입니다. 지원 모델: {valid_models}')
        return v
    
    @validator('port')
    def validate_port(cls, v):
        """포트 번호 검증"""
        if v < 1024 or v > 65535:
            raise ValueError('포트 번호는 1024-65535 사이여야 합니다.')
        return v
    
    class Config:
        """Pydantic 설정"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra_forbidden = False
        # 환경 변수 예시
        schema_extra = {
            "example": {
                "api_title": "Cherry AI - Vertex AI LLM Server",
                "api_version": "1.0.0",
                "host": "0.0.0.0",
                "port": 8000,
                "google_ai_model": "gemini-pro",
                "default_temperature": 0.7,
                "default_max_tokens": 1000
            }
        }

# 전역 설정 인스턴스
settings = Settings()

# API 키 검증
if not settings.google_api_key:
    raise ValueError("GOOGLE_API_KEY environment variable is required") 