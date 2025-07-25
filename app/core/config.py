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
        ## Cherry AI - 발달장애인을 위한 내비게이션 챗봇
        
        발달장애인과 경계선 지능인을 위한 친근하고 이해하기 쉬운 내비게이션 도우미입니다.
        
        ### 주요 기능
        - 🗺️ 길을 이탈했을 때 즉시 해결책 제공
        - 🚌 대중교통을 놓쳤을 때 대안 경로 안내
        - 🆘 긴급 상황에서 안전한 해결책 제시
        - 💬 사회적 상호작용을 통한 도움 요청 방법 안내
        - 🧠 발달장애인과 경계선 지능인에 특화된 간단하고 명확한 답변
        
        ### 지원 상황
        - 길 이탈 상황
        - 버스/지하철 놓침 상황
        - 긴급 상황 (어두운 곳에서 길 잃음 등)
        - 일반 길 찾기
        
        ### 사용 방법
        1. 현재 위치 정보를 입력하세요
        2. 목적지 주소를 입력하세요 (선택사항)
        3. 이동 수단을 선택하세요 (도보/대중교통)
        4. 상황을 설명하세요
        5. 즉시 해결책을 받으세요
        
        ### 특징
        - 단발성 완결 답변으로 추가 질문 불필요
        - 구현되지 않은 기능 언급 제거
        - 주변 사람에게 도움 요청하는 구체적 방법 제시
        - 발달장애인 친화적 언어 사용
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
        default=0.2, 
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