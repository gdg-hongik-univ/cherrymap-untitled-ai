"""
채팅 API 엔드포인트

이 모듈은 Google AI Studio와의 채팅을 위한 API 엔드포인트를 정의합니다.
메시지를 받아서 Google AI Studio에 전달하고 응답을 반환하는 기능을 제공합니다.
"""

import logging
from fastapi import APIRouter, HTTPException, status
from app.models.schemas import ChatRequest, ChatResponse
from app.services.google_ai_service import google_ai_service

# 로거 설정
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/chat", response_model=ChatResponse, tags=["chat"])
async def chat_with_google_ai(request: ChatRequest):
    """
    ## Google AI Studio와 채팅
    
    메시지를 받아서 Google AI Studio에 전달하고 응답을 반환하는 엔드포인트입니다.
    
    ### 요청 파라미터
    - **message**: Google AI Studio에게 전달할 메시지 (필수)
    
    ### 응답
    - **response**: Google AI Studio로부터 받은 응답
    - **model**: 사용된 AI 모델명
    
    ### 사용 예시
    ```bash
    curl -X POST "http://localhost:8000/chat" \\
         -H "Content-Type: application/json" \\
         -d '{
           "message": "안녕하세요! 간단한 자기소개를 해주세요."
         }'
    ```
    
    ### 응답 예시
    ```json
    {
        "response": "안녕하세요! 저는 Google의 Gemini 모델입니다...",
        "model": "gemini-1.5-flash"
    }
    ```
    
    ### 오류 코드
    - `500`: Google AI Studio 통신 오류
    - `422`: 요청 데이터 검증 오류
    """
    try:
        logger.info(f"채팅 요청 수신. 메시지: {request.message[:50]}...")
        
        # Google AI Studio 서비스를 통해 응답 생성
        response = await google_ai_service.generate_response(request)
        
        logger.info(f"채팅 응답 생성 완료. 응답 길이: {len(response.response)}")
        
        return response
        
    except Exception as e:
        logger.error(f"채팅 요청 처리 중 오류 발생: {str(e)}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error communicating with Google AI Studio: {str(e)}"
        ) 