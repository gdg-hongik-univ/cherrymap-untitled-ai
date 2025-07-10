# Python 3.10 슬림 이미지 사용
FROM python:3.10-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치 (보안 강화)
RUN apt-get update && apt-get install -y \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 파일 복사
COPY requirements.txt .

# Python 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 소스 코드 복사
COPY . .

# 포트 8000 노출 (FastAPI 기본 포트)
EXPOSE 8000

# 환경변수 설정 (프로덕션용 고정값)
ENV HOST=0.0.0.0
ENV PORT=8000
ENV DEBUG=false

# 애플리케이션 실행 명령
CMD ["python", "main.py"]