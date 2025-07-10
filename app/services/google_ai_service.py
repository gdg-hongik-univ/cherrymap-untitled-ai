"""
Google AI Studio 서비스 모듈

이 모듈은 Google AI Studio와의 통신을 담당합니다.
채팅 요청 처리, 응답 생성, 헬스 체크 등의 기능을 제공합니다.
"""

import logging
from typing import Optional
import google.generativeai as genai
from app.core.config import settings
from app.models.schemas import ChatRequest, ChatResponse

# 로거 설정
logger = logging.getLogger(__name__)

class GoogleAIService:
    """
    Google AI Studio 서비스 클래스
    
    Google AI Studio와의 통신을 담당하는 서비스 클래스입니다.
    채팅 요청 처리, 응답 생성, 헬스 체크 등의 기능을 제공합니다.
    """
    
    def __init__(self):
        """
        Google AI Studio 서비스 초기화
        
        Google AI Studio API 키를 설정하고 모델을 초기화합니다.
        """
        try:
            # Google AI Studio 설정
            genai.configure(api_key=settings.google_api_key)
            
            # 모델 초기화
            self.model = genai.GenerativeModel(settings.google_ai_model)
            
            logger.info(f"Google AI Studio 서비스 초기화 완료. 모델: {settings.google_ai_model}")
            
        except Exception as e:
            logger.error(f"Google AI Studio 서비스 초기화 실패: {str(e)}")
            raise
    
    async def generate_response(self, request: ChatRequest) -> ChatResponse:
        """
        Google AI Studio로부터 응답 생성
        
        Args:
            request (ChatRequest): 채팅 요청 객체
            
        Returns:
            ChatResponse: Google AI Studio 응답
            
        Raises:
            Exception: Google AI Studio 통신 오류
            
        Example:
            >>> request = ChatRequest(message="안녕하세요!")
            >>> response = await service.generate_response(request)
            >>> print(response.response)
        """
        try:
            logger.info(f"Google AI Studio 요청 시작. 메시지 길이: {len(request.message)}")
            
            # Google AI Studio에 요청 전송 (고정된 설정 사용)
            response = self.model.generate_content(
                request.message,
                generation_config=genai.types.GenerationConfig(
                    temperature=settings.default_temperature,  # 0.3으로 고정
                    max_output_tokens=settings.default_max_tokens  # 1000으로 고정
                )
            )
            
            logger.info(f"Google AI Studio 응답 생성 완료. 응답 길이: {len(response.text)}")
            
            return ChatResponse(
                response=response.text,
                model=settings.google_ai_model
            )
            
        except Exception as e:
            logger.error(f"Google AI Studio 통신 오류: {str(e)}")
            raise Exception(f"Google AI Studio 통신 오류: {str(e)}")
    
    async def health_check(self) -> bool:
        """
        Google AI Studio 서비스 헬스 체크
        
        간단한 테스트 요청을 보내서 서비스가 정상 작동하는지 확인합니다.
        
        Returns:
            bool: 서비스 상태 (True: 정상, False: 오류)
            
        Example:
            >>> is_healthy = await service.health_check()
            >>> print(f"서비스 상태: {'정상' if is_healthy else '오류'}")
        """
        try:
            logger.debug("Google AI Studio 헬스 체크 시작")
            
            # 간단한 테스트 요청
            test_response = self.model.generate_content("Hello")
            
            logger.debug("Google AI Studio 헬스 체크 성공")
            return True
            
        except Exception as e:
            logger.error(f"Google AI Studio 헬스 체크 실패: {str(e)}")
            return False
    
    def get_model_info(self) -> dict:
        """
        현재 사용 중인 모델 정보 반환
        
        현재 설정된 모델과 기본 파라미터 정보를 반환합니다.
        
        Returns:
            dict: 모델 정보
            
        Example:
            >>> info = service.get_model_info()
            >>> print(f"모델: {info['model']}")
            >>> print(f"기본 temperature: {info['temperature_default']}")
        """
        return {
            "model": settings.google_ai_model,
            "temperature_default": settings.default_temperature,
            "max_tokens_default": settings.default_max_tokens,
            "supported_models": [
                'gemini-1.5-flash',
                'gemini-1.5-pro',
                'gemini-pro',
                'gemini-pro-vision'
            ]
        }
    
    def get_service_status(self) -> dict:
        """
        서비스 상태 정보 반환
        
        서비스의 현재 상태와 설정 정보를 반환합니다.
        
        Returns:
            dict: 서비스 상태 정보
        """
        return {
            "service_name": "Google AI Studio Service",
            "model": settings.google_ai_model,
            "api_configured": bool(settings.google_api_key),
            "default_settings": {
                "temperature": settings.default_temperature,
                "max_tokens": settings.default_max_tokens
            }
        }

# 전역 서비스 인스턴스
google_ai_service = GoogleAIService() 