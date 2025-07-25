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
            
            # 시스템 프롬프트 정의
            self.system_prompt = """
당신은 정확하고 신뢰할 수 있는 AI 어시스턴트입니다. 다음 지침을 엄격히 따르세요:

**핵심 원칙:**
1. **정확성 우선**: 확실하지 않은 정보는 절대 제공하지 마세요. "확실하지 않습니다"라고 솔직히 답변하세요.
2. **간결성**: 불필요한 말을 하지 말고 핵심만 답변하세요.
3. **논리성**: 논리적이고 일관된 답변을 제공하세요.
4. **객관성**: 주관적인 의견보다는 사실에 기반한 답변을 하세요.
5. **헛소리 금지**: 추측, 상상, 또는 확실하지 않은 정보로 답변하지 마세요.

**답변 스타일:**
- 명확하고 이해하기 쉽게 답변하세요
- 필요시 구체적인 예시를 제공하세요
- 복잡한 주제는 단계별로 설명하세요
- 사용자의 질문에 직접적으로 답변하세요

**금지사항:**
- 확실하지 않은 정보 제공
- 과도하게 긴 답변
- 주관적인 의견을 사실처럼 표현
- 추측이나 상상으로 답변

사용자의 질문에 정확하고 유용한 답변을 제공하세요.
"""
            
            # 모델 초기화 (구버전 호환)
            self.model = genai.GenerativeModel(settings.google_ai_model)
            
            logger.info(f"Google AI Studio 서비스 초기화 완료. 모델: {settings.google_ai_model}")
            
        except Exception as e:
            logger.error(f"Google AI Studio 서비스 초기화 실패: {str(e)}")
            raise
    
    def _preprocess_prompt(self, message: str) -> str:
        """
        사용자 메시지를 전처리하여 더 나은 응답을 생성하도록 개선
        
        Args:
            message (str): 원본 사용자 메시지
            
        Returns:
            str: 전처리된 메시지
        """
        # 메시지 정규화
        message = message.strip()
        
        # 메시지가 너무 짧은 경우 구체적인 요청으로 변환
        if len(message) < 10:
            return f"다음 질문에 대해 정확하고 간결하게 답변해주세요: {message}"
        
        # 메시지가 너무 긴 경우 요약 요청
        if len(message) > 500:
            return f"다음 긴 질문에 대해 핵심만 간결하게 답변해주세요: {message[:500]}..."
        
        # 특정 질문 유형에 대한 프롬프트 개선
        lower_message = message.lower()
        
        # 사실 확인 질문
        if any(keyword in lower_message for keyword in ['맞나요', '맞는가', '정확한가', '사실인가']):
            return f"다음 질문에 대해 사실에 기반하여 정확하게 답변해주세요. 확실하지 않으면 '확실하지 않습니다'라고 답변하세요: {message}"
        
        # 의견 요청 질문
        if any(keyword in lower_message for keyword in ['어떻게 생각하나요', '의견', '생각']):
            return f"다음 질문에 대해 객관적이고 균형잡힌 관점에서 답변해주세요: {message}"
        
        # 설명 요청 질문
        if any(keyword in lower_message for keyword in ['설명', '이해', '알려주세요', '무엇인가']):
            return f"다음 질문에 대해 명확하고 이해하기 쉽게 설명해주세요: {message}"
        
        # 비교 질문
        if any(keyword in lower_message for keyword in ['차이', '비교', 'vs', 'versus']):
            return f"다음 질문에 대해 객관적인 사실에 기반하여 비교해주세요: {message}"
        
        return message
    
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
            
            # 메시지 전처리
            processed_message = self._preprocess_prompt(request.message)
            
            # 시스템 프롬프트와 사용자 메시지 결합
            full_prompt = f"{self.system_prompt}\n\n사용자 질문: {processed_message}\n\n답변:"
            
            # Google AI Studio에 요청 전송 (고정된 설정 사용)
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=settings.default_temperature,  # 0.2로 낮춤
                    max_output_tokens=settings.default_max_tokens,  # 1000으로 고정
                    top_p=0.8,  # 더 일관된 응답을 위해 추가
                    top_k=40,   # 더 일관된 응답을 위해 추가
                    candidate_count=1  # 단일 응답만 생성
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