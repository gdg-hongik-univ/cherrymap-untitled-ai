"""
내비게이션 챗봇 서비스 모듈

발달장애인과 경계선 지능인을 위한 지도 챗봇 서비스입니다.
길 이탈, 대중교통 놓침 등의 상황에 대한 도움을 제공합니다.
"""

import logging
from typing import Optional, Dict, Any
import google.generativeai as genai
from app.core.config import settings
from app.models.schemas import NavigationChatRequest, NavigationChatResponse, LocationInfo

# 로거 설정
logger = logging.getLogger(__name__)

class NavigationChatbotService:
    """
    내비게이션 챗봇 서비스 클래스
    
    발달장애인과 경계선 지능인을 위한 지도 챗봇 서비스입니다.
    Tmap API와 연동하여 실질적인 도움을 제공합니다.
    """
    
    def __init__(self):
        """
        내비게이션 챗봇 서비스 초기화
        """
        try:
            # Google AI Studio 설정
            genai.configure(api_key=settings.google_api_key)
            
            # 발달장애인/경계선 지능인 특화 시스템 프롬프트
            self.system_prompt = """
당신은 발달장애인과 경계선 지능인을 위한 친근하고 이해하기 쉬운 내비게이션 도우미입니다.

**핵심 역할:**
- 길을 잃었거나 대중교통을 놓친 사용자에게 즉시 해결책을 제공
- 홈 화면에서의 일반적인 대화나 도움 요청에 친근하게 응답
- 추가 질문이나 대화 없이 완결된 답변 제공
- 감정적 지원과 실질적 해결책을 함께 제시

**답변 원칙:**
1. **완결된 답변**: 추가 질문 없이 즉시 해결책 제시
2. **구체적 방법**: 실제로 할 수 있는 행동을 명확히 안내
3. **안심시키기**: "괜찮아요", "함께 해요" 등 안심 표현
4. **사회적 상호작용**: 주변 사람에게 도움 요청하는 방법 제시

**주요 상황별 완결 답변:**

**홈 화면 일반 대화:**
- "안녕하세요! 무엇을 도와드릴까요?"
- "궁금한 것이 있으시면 언제든 말씀해주세요"
- "길을 잃거나 교통수단을 놓쳤을 때 도움이 필요하시면 말씀해주세요"
- "안전하게 이동하는 방법을 알려드릴 수 있어요"

**길 이탈 상황:**
- "괜찮아요! 함께 올바른 길을 찾아요"
- 목적지가 있으면: "주변에 있는 사람에게 '[목적지명]으로 가는 길 알려주세요'라고 말해보세요"
- 목적지가 없으면: "주변에 있는 사람에게 '도와주세요'라고 말해보세요"
- "가장 가까운 지하철역/버스정류장으로 가세요"
- "역/정류장에서 안내데스크에 물어보세요"

**대중교통 놓침 상황:**
- "괜찮아요! 다음 교통수단이 곧 올 거예요"
- "정류장에 앉아서 기다려주세요"
- "주변에 있는 사람에게 '다음 버스 언제 오나요?'라고 물어보세요"
- "지하철역까지 걸어갈 수 있어요"

**긴급 상황:**
- "괜찮아요! 함께 안전한 곳으로 가요"
- "밝은 곳으로 천천히 걸어가세요"
- "주변에 있는 사람에게 '도와주세요'라고 말해보세요"
- "112에 전화해주세요"

**응답 규칙:**
- 추가 질문 금지 (예: "어디에 계신지 알려주세요")
- 즉시 해결책 제시
- 구체적이고 실행 가능한 방법만 안내
- 목적지 정보가 있으면 구체적인 목적지명을 사용
- 주변 사람에게 도움 요청하는 구체적 문구 제시
- 소괄호나 예시 사용 금지
- 추상적 설명 금지
- 문장은 짧고 명확하게
- 복잡한 단어 사용 금지
- 구현되지 않은 기능 언급 금지 (지도, 앱 등)

**금지사항:**
- "~를 알려주세요", "~를 말씀해주세요" 등의 질문
- "지도를 보여드릴게요", "앱을 사용하세요" 등 구현되지 않은 기능
- 소괄호 () 사용
- "예시로", "예를 들어" 등의 표현
- 복잡한 설명
- 추상적 개념
- 긴 문장
- 기술적 용어
- 대화 이어가기 요구

사용자가 안전하고 편안하게 목적지에 도착할 수 있도록 즉시 완결된 해결책을 제공하세요.
"""
            
            # 모델 초기화
            self.model = genai.GenerativeModel(settings.google_ai_model)
            
            logger.info("내비게이션 챗봇 서비스 초기화 완료")
            
        except Exception as e:
            logger.error(f"내비게이션 챗봇 서비스 초기화 실패: {str(e)}")
            raise
    
    def _analyze_situation(self, request: NavigationChatRequest) -> Dict[str, Any]:
        """
        사용자 상황을 분석하여 적절한 대응 전략을 결정
        
        Args:
            request (NavigationChatRequest): 사용자 요청
            
        Returns:
            Dict[str, Any]: 상황 분석 결과
        """
        message = request.message.lower()
        context = request.user_context.lower() if request.user_context else ""
        
        # 상황 분석
        situation = {
            "type": "unknown",
            "urgency": "low",
            "needs_reassurance": True,
            "suggested_actions": []
        }
        
        # 홈 화면 일반 대화 감지
        if request.mode == "홈":
            situation["type"] = "home_conversation"
            situation["urgency"] = "low"
            situation["needs_reassurance"] = False
            situation["suggested_actions"] = [
                "general_conversation",
                "provide_guidance"
            ]
            return situation
        
        # 길 이탈 상황 감지
        if any(keyword in message for keyword in ['길을 이탈', '길을 잃었', '잘못된 길', '길을 못 찾']):
            situation["type"] = "route_deviation"
            situation["urgency"] = "medium"
            situation["suggested_actions"] = [
                "recalculate_route",
                "find_nearby_landmarks",
                "provide_step_by_step_guidance"
            ]
        
        # 대중교통 놓침 상황 감지
        elif any(keyword in message or keyword in context for keyword in ['버스를 놓쳤', '지하철을 놓쳤', '교통수단을 놓쳤']):
            situation["type"] = "missed_transport"
            situation["urgency"] = "medium"
            situation["suggested_actions"] = [
                "find_next_transport",
                "suggest_alternative_routes",
                "provide_wait_time_info"
            ]
        
        # 긴급 상황 감지
        elif any(keyword in message for keyword in ['무서워', '도와주세요', '긴급', '위험']):
            situation["type"] = "emergency"
            situation["urgency"] = "high"
            situation["needs_reassurance"] = True
            situation["suggested_actions"] = [
                "emergency_help",
                "find_safe_location",
                "contact_emergency_services"
            ]
        
        return situation
    
    def _create_contextual_prompt(self, request: NavigationChatRequest, situation: Dict[str, Any]) -> str:
        """
        상황에 맞는 컨텍스트 프롬프트 생성
        
        Args:
            request (NavigationChatRequest): 사용자 요청
            situation (Dict[str, Any]): 상황 분석 결과
            
        Returns:
            str: 컨텍스트 프롬프트
        """
        # 기본 정보 (간단하게)
        context_parts = [
            f"위치: {request.location.latitude}, {request.location.longitude}",
        ]
        
        # mode가 "홈"이 아닐 때만 이동수단 정보 추가
        if request.mode != "홈":
            context_parts.append(f"이동수단: {request.mode}")
        else:
            context_parts.append("상황: 홈 화면에서의 일반 대화")
        
        if request.destination_address:
            context_parts.append(f"목적지: {request.destination_address}")
            context_parts.append("중요: 목적지 정보가 있으므로 구체적인 목적지명을 사용하여 답변하세요")
        else:
            context_parts.append("목적지: 정보 없음")
            context_parts.append("중요: 목적지 정보가 없으므로 일반적인 도움 요청 방법을 제시하세요")
        
        if request.user_context:
            context_parts.append(f"상황: {request.user_context}")
        
        # 상황별 즉시 해결책 지침
        if situation["type"] == "home_conversation":
            context_parts.append("상황: 홈 화면 일반 대화. 친근하고 도움이 되는 답변 제공")
        elif situation["type"] == "route_deviation":
            context_parts.append("상황: 길을 이탈함. 즉시 새로운 경로 안내")
        elif situation["type"] == "missed_transport":
            context_parts.append("상황: 교통수단 놓침. 즉시 다음 교통수단 정보 제공")
        elif situation["type"] == "emergency":
            context_parts.append("상황: 긴급상황. 즉시 안전 조치 안내")
        
        context_parts.append("중요: 추가 질문 없이 즉시 완결된 해결책만 제공")
        
        return "\n".join(context_parts)
    
    async def generate_navigation_response(self, request: NavigationChatRequest) -> NavigationChatResponse:
        """
        내비게이션 챗봇 응답 생성
        
        Args:
            request (NavigationChatRequest): 내비게이션 챗봇 요청
            
        Returns:
            NavigationChatResponse: 챗봇 응답
        """
        try:
            logger.info(f"내비게이션 챗봇 요청 수신: {request.message}")
            
            # 상황 분석
            situation = self._analyze_situation(request)
            
            # 컨텍스트 프롬프트 생성
            context_prompt = self._create_contextual_prompt(request, situation)
            
            # 전체 프롬프트 구성
            full_prompt = f"""
{self.system_prompt}

현재 상황:
{context_prompt}

사용자: {request.message}

발달장애인과 경계선 지능인에게 적합한 매우 간단하고 명확한 답변을 제공하세요.
"""
            
            # AI 응답 생성
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,  # 일관성과 창의성의 균형
                    max_output_tokens=800,
                    top_p=0.8,
                    top_k=40,
                    candidate_count=1
                )
            )
            
            # 응답 후처리
            response_text = response.text.strip()
            
            # 액션 타입 결정
            action_type = situation["suggested_actions"][0] if situation["suggested_actions"] else None
            
            # 신뢰도 점수 계산 (상황의 명확성에 기반)
            confidence_score = 0.9 if situation["type"] != "unknown" else 0.7
            
            logger.info(f"내비게이션 챗봇 응답 생성 완료. 액션: {action_type}")
            
            return NavigationChatResponse(
                response=response_text,
                model=settings.google_ai_model,
                action_type=action_type,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            logger.error(f"내비게이션 챗봇 응답 생성 실패: {str(e)}")
            raise Exception(f"내비게이션 챗봇 오류: {str(e)}")

# 전역 서비스 인스턴스
navigation_chatbot_service = NavigationChatbotService() 