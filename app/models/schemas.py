"""
API 요청/응답 스키마 정의

이 모듈은 Cherry AI LLM Server의 모든 API 요청/응답 스키마를 정의합니다.
Pydantic을 사용하여 데이터 검증과 자동 문서화를 제공합니다.
"""

from typing import Optional
from pydantic import BaseModel, Field, validator

# ==================== 요청 스키마 ====================

class ChatRequest(BaseModel):
    """
    채팅 요청 스키마
    
    Google AI Studio와의 채팅을 위한 요청 데이터 구조를 정의합니다.
    """
    message: str = Field(
        ...,
        description="Google AI Studio에게 전달할 메시지",
        example="안녕하세요! 오늘 날씨는 어때요?",
        min_length=1,
        max_length=10000
    )
    
    @validator('message')
    def validate_message(cls, v):
        """메시지 검증"""
        if not v.strip():
            raise ValueError('메시지는 비어있을 수 없습니다.')
        return v.strip()
    
    class Config:
        """Pydantic 설정"""
        schema_extra = {
            "example": {
                "message": "안녕하세요! 간단한 자기소개를 해주세요."
            }
        }

# ==================== 응답 스키마 ====================

class ChatResponse(BaseModel):
    """
    채팅 응답 스키마
    
    Google AI Studio로부터 받은 응답 데이터 구조를 정의합니다.
    """
    response: str = Field(
        ...,
        description="Google AI Studio로부터 받은 응답",
        example="안녕하세요! 저는 Google의 Gemini 모델입니다. 무엇을 도와드릴까요?"
    )
    model: str = Field(
        default="gemini-1.5-flash",
        description="사용된 AI 모델명"
    )
    
    class Config:
        """Pydantic 설정"""
        schema_extra = {
            "example": {
                "response": "안녕하세요! 저는 Google의 Gemini 모델입니다. 무엇을 도와드릴까요?",
                "model": "gemini-1.5-flash"
            }
        }

class ServerStatus(BaseModel):
    """
    서버 상태 스키마
    
    서버의 현재 상태 정보를 반환하는 스키마입니다.
    """
    message: str = Field(
        description="서버 상태 메시지"
    )
    model: str = Field(
        description="사용 중인 AI 모델"
    )
    status: str = Field(
        description="서버 상태 (active/inactive)"
    )
    
    class Config:
        """Pydantic 설정"""
        schema_extra = {
            "example": {
                "message": "Cherry AI - Vertex AI LLM Server is running!",
                "model": "gemini-pro",
                "status": "active"
            }
        }

class HealthStatus(BaseModel):
    """
    헬스 체크 스키마
    
    서버의 헬스 상태를 확인하는 스키마입니다.
    """
    status: str = Field(
        description="서버 헬스 상태 (healthy/unhealthy)"
    )
    model: str = Field(
        description="사용 중인 AI 모델"
    )
    
    class Config:
        """Pydantic 설정"""
        schema_extra = {
            "example": {
                "status": "healthy",
                "model": "gemini-pro"
            }
        }

class ErrorResponse(BaseModel):
    """
    에러 응답 스키마
    
    API 오류 발생 시 반환되는 에러 정보 스키마입니다.
    """
    detail: str = Field(
        description="에러 상세 메시지"
    )
    error_code: Optional[str] = Field(
        default=None,
        description="에러 코드"
    )
    
    class Config:
        """Pydantic 설정"""
        schema_extra = {
            "example": {
                "detail": "Vertex AI 통신 오류: API 키가 유효하지 않습니다.",
                "error_code": "VERTEX_AI_ERROR"
            }
        } 