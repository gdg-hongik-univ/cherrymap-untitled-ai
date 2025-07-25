"""
내비게이션 챗봇 API 엔드포인트

발달장애인과 경계선 지능인을 위한 지도 챗봇 API 엔드포인트입니다.
길 이탈, 대중교통 놓침 등의 상황에 대한 도움을 제공합니다.
"""

import logging
from fastapi import APIRouter, HTTPException, status
from app.models.schemas import NavigationChatRequest, NavigationChatResponse
from app.services.navigation_chatbot_service import navigation_chatbot_service

# 로거 설정
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/navigation/chat", response_model=NavigationChatResponse, tags=["navigation"])
async def navigation_chat(request: NavigationChatRequest):
    """
    ## 내비게이션 챗봇
    
    발달장애인과 경계선 지능인을 위한 지도 챗봇 엔드포인트입니다.
    길 이탈, 대중교통 놓침 등의 상황에 대한 친근하고 이해하기 쉬운 도움을 제공합니다.
    
    ### 요청 파라미터
    - **message**: 사용자의 질문이나 도움 요청 메시지 (필수)
    - **location**: 사용자의 현재 위치 정보 (필수)
      - **latitude**: 위도 (-90.0 ~ 90.0)
      - **longitude**: 경도 (-180.0 ~ 180.0)
    - **destination_address**: 목적지 주소 (선택사항)
    - **transportation_mode**: 이동 수단 (선택사항, 기본값: public_transport)
      - public_transport: 대중교통
      - walking: 도보
      - driving: 자동차
    - **user_context**: 사용자 상황 설명 (선택사항)
    
    ### 응답
    - **response**: 챗봇의 답변 메시지
    - **model**: 사용된 AI 모델명
    - **action_type**: 제안하는 액션 타입
    - **confidence_score**: 응답의 신뢰도 점수 (0.0 ~ 1.0)
    
    ### 사용 예시
    ```bash
    curl -X POST "http://localhost:8000/navigation/chat" \\
         -H "Content-Type: application/json" \\
         -d '{
           "message": "길을 이탈했어요",
           "location": {
             "latitude": 37.5665,
             "longitude": 126.9780
           },
           "destination_address": "서울시 강남구 테헤란로 123",
           "transportation_mode": "public_transport",
           "user_context": "지하철을 놓쳤어요"
         }'
    ```
    
    ### 응답 예시
    ```json
    {
        "response": "걱정하지 마세요! 함께 올바른 길을 찾아요. 현재 위치에서 가장 가까운 지하철역을 찾아드릴게요.",
        "model": "gemini-1.5-flash",
        "action_type": "recalculate_route",
        "confidence_score": 0.95
    }
    ```
    
    ### 오류 코드
    - `500`: 내비게이션 챗봇 통신 오류
    - `422`: 요청 데이터 검증 오류
    """
    try:
        logger.info(f"내비게이션 챗봇 요청 수신. 메시지: {request.message[:50]}...")
        logger.info(f"위치: ({request.location.latitude}, {request.location.longitude})")
        
        # 내비게이션 챗봇 서비스를 통해 응답 생성
        response = await navigation_chatbot_service.generate_navigation_response(request)
        
        logger.info(f"내비게이션 챗봇 응답 생성 완료. 액션: {response.action_type}")
        
        return response
        
    except Exception as e:
        logger.error(f"내비게이션 챗봇 요청 처리 중 오류 발생: {str(e)}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Navigation chatbot error: {str(e)}"
        )

@router.get("/navigation/health", tags=["navigation"])
async def navigation_health_check():
    """
    ## 내비게이션 챗봇 헬스 체크
    
    내비게이션 챗봇 서비스의 상태를 확인합니다.
    
    ### 응답
    - **status**: 서비스 상태 (healthy/unhealthy)
    - **service**: 서비스명
    """
    try:
        # 간단한 테스트 요청으로 서비스 상태 확인
        test_request = NavigationChatRequest(
            message="테스트",
            location={"latitude": 37.5665, "longitude": 126.9780}
        )
        
        await navigation_chatbot_service.generate_navigation_response(test_request)
        
        return {
            "status": "healthy",
            "service": "Navigation Chatbot Service"
        }
        
    except Exception as e:
        logger.error(f"내비게이션 챗봇 헬스 체크 실패: {str(e)}")
        
        return {
            "status": "unhealthy",
            "service": "Navigation Chatbot Service",
            "error": str(e)
        } 