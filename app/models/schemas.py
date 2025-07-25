"""
API 요청/응답 스키마 정의

이 모듈은 Cherry AI LLM Server의 모든 API 요청/응답 스키마를 정의합니다.
Pydantic을 사용하여 데이터 검증과 자동 문서화를 제공합니다.
"""

from typing import Optional
from pydantic import BaseModel, Field, validator

# ==================== 공통 스키마 ====================

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
                "message": "Cherry AI - 발달장애인을 위한 내비게이션 챗봇 서버가 실행 중입니다!",
                "model": "gemini-1.5-flash",
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

# ==================== 지도 챗봇 스키마 ====================

class LocationInfo(BaseModel):
    """
    위치 정보 스키마
    
    사용자의 현재 위치 정보를 담는 스키마입니다.
    """
    latitude: float = Field(
        ...,
        description="위도 (latitude)",
        ge=-90.0,
        le=90.0,
        example=37.5665
    )
    longitude: float = Field(
        ...,
        description="경도 (longitude)",
        ge=-180.0,
        le=180.0,
        example=126.9780
    )
    
    @validator('latitude')
    def validate_latitude(cls, v):
        """위도 검증"""
        if v < -90 or v > 90:
            raise ValueError('위도는 -90에서 90 사이여야 합니다.')
        return v
    
    @validator('longitude')
    def validate_longitude(cls, v):
        """경도 검증"""
        if v < -180 or v > 180:
            raise ValueError('경도는 -180에서 180 사이여야 합니다.')
        return v

class NavigationChatRequest(BaseModel):
    """
    내비게이션 챗봇 요청 스키마
    
    발달장애인과 경계선 지능인을 위한 지도 챗봇 요청 데이터 구조를 정의합니다.
    """
    message: str = Field(
        ...,
        description="사용자의 질문이나 도움 요청 메시지",
        example="길을 이탈했어요",
        min_length=1,
        max_length=1000
    )
    location: LocationInfo = Field(
        ...,
        description="사용자의 현재 위치 정보"
    )
    destination_address: Optional[str] = Field(
        default=None,
        description="목적지 주소 (선택사항)",
        example="서울시 강남구 테헤란로 123"
    )
    mode: Optional[str] = Field(
        default="대중교통",
        description="이동 수단 (도보, 대중교통)"
    )
    user_context: Optional[str] = Field(
        default=None,
        description="사용자 상황 설명 (선택사항)",
        example="지하철을 놓쳤어요"
    )
    
    @validator('message')
    def validate_message(cls, v):
        """메시지 검증"""
        if not v.strip():
            raise ValueError('메시지는 비어있을 수 없습니다.')
        return v.strip()
    
    @validator('mode')
    def validate_mode(cls, v):
        """이동 수단 검증"""
        valid_modes = ['도보', '대중교통']
        if v not in valid_modes:
            raise ValueError(f'지원하지 않는 이동 수단입니다. 지원: {valid_modes}')
        return v
    
    class Config:
        """Pydantic 설정"""
        schema_extra = {
            "example": {
                "message": "길을 이탈했어요",
                "location": {
                    "latitude": 37.5665,
                    "longitude": 126.9780
                },
                "destination_address": "서울시 강남구 테헤란로 123",
                "mode": "대중교통",
                "user_context": "지하철을 놓쳤어요"
            }
        }

class NavigationChatResponse(BaseModel):
    """
    내비게이션 챗봇 응답 스키마
    
    발달장애인과 경계선 지능인을 위한 지도 챗봇 응답 데이터 구조를 정의합니다.
    """
    response: str = Field(
        ...,
        description="챗봇의 답변 메시지"
    )
    model: str = Field(
        default="gemini-1.5-flash",
        description="사용된 AI 모델명"
    )
    action_type: Optional[str] = Field(
        default=None,
        description="제안하는 액션 타입 (recalculate_route, find_nearby_station, emergency_help, etc.)"
    )
    confidence_score: Optional[float] = Field(
        default=None,
        description="응답의 신뢰도 점수 (0.0 ~ 1.0)",
        ge=0.0,
        le=1.0
    )
    
    class Config:
        """Pydantic 설정"""
        schema_extra = {
            "example": {
                "response": "걱정하지 마세요! 현재 위치에서 가장 가까운 지하철역을 찾아드릴게요.",
                "model": "gemini-1.5-flash",
                "action_type": "find_nearby_station",
                "confidence_score": 0.95
            }
        } 