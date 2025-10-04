# 트러블슈팅 가이드

## Docker Compose 환경 설정 문제 해결

### 1. LocalStack 포트 충돌 (Port 4566)

**문제:**
```
ERROR: for localstack  Cannot start service localstack: ports are not available:
exposing port TCP 0.0.0.0:4566 -> 127.0.0.1:0: listen tcp 0.0.0.0:4566:
bind: An attempt was made to access a socket in a way forbidden by its access permissions.
```

**원인:**
- Windows 환경에서 포트 4000-5000 범위가 시스템에 의해 예약될 수 있음
- 특히 Hyper-V, WSL2, Docker Desktop 사용 시 발생

**해결:**
1. LocalStack 포트를 14566으로 변경
2. `docker-compose.yml` 수정:
   ```yaml
   localstack:
     ports:
       - "${LOCALSTACK_PORT:-14566}:4566"
   ```
3. `.env.example` 업데이트:
   ```bash
   LOCALSTACK_PORT=14566  # Changed to avoid Windows reserved port range
   ```

**참고:**
- 컨테이너 내부에서는 여전히 4566 포트 사용
- 호스트에서 접속할 때만 14566 포트 사용
- AWS SDK 설정: `AWS_ENDPOINT_URL=http://localstack:4566` (컨테이너 간 통신)

---

### 2. LocalStack 볼륨 마운트 오류

**문제:**
```
ERROR: 'rm -rf "/tmp/localstack"': exit code 1;
output: b"rm: cannot remove '/tmp/localstack': Device or resource busy\n"
OSError: [Errno 16] Device or resource busy: '/tmp/localstack'
```

**원인:**
- `/tmp/localstack` 디렉토리가 Docker 볼륨과 충돌
- LocalStack 초기화 시 임시 디렉토리 정리 실패

**해결:**
1. 볼륨 마운트 경로 변경
2. `docker-compose.yml` 수정:
   ```yaml
   localstack:
     environment:
       DATA_DIR: /var/lib/localstack  # Changed from /tmp/localstack/data
     volumes:
       - localstack_data:/var/lib/localstack  # Changed from /tmp/localstack
   ```

---

### 3. DynamoDB Local Healthcheck 실패

**문제:**
```
dailydevq-dynamodb   Up (unhealthy)   0.0.0.0:8000->8000/tcp
```

**원인:**
- DynamoDB Local은 인증 없는 요청에 `MissingAuthenticationToken` 에러 반환
- 기존 healthcheck가 HTTP 200 응답만 기대함

**해결:**
1. Healthcheck를 DynamoDB 응답 메시지 확인으로 변경
2. `docker-compose.yml` 수정:
   ```yaml
   dynamodb-local:
     healthcheck:
       test: ["CMD-SHELL", "curl -s http://localhost:8000 | grep -q 'MissingAuthenticationToken' || exit 1"]
   ```

**테스트:**
```bash
curl http://localhost:8000
# 응답: {"__type":"com.amazonaws.dynamodb.v20120810#MissingAuthenticationToken","Message":"..."}
```

---

### 4. Backend 포트 충돌 (Port 8000)

**문제:**
```
ERROR: for backend  Cannot start service backend: failed to set up container networking:
Bind for 0.0.0.0:8000 failed: port is already allocated
```

**원인:**
- DynamoDB Local이 이미 8000 포트 사용 중
- Backend도 기본 8000 포트 설정

**해결:**
1. Backend 포트를 8001로 변경
2. `docker-compose.yml` 수정:
   ```yaml
   backend:
     ports:
       - "${BACKEND_PORT:-8001}:8000"
   ```
3. `.env.example` 업데이트:
   ```bash
   BACKEND_PORT=8001  # Changed from 8000 to avoid conflict with DynamoDB Local
   ```

---

### 5. Docker Network 재생성 필요

**문제:**
```
Network "dailydevq-shared" needs to be recreated - option "com.docker.network.enable_ipv4" has changed
```

**원인:**
- docker-compose.yml 변경 후 네트워크 설정 불일치
- 실행 중인 컨테이너가 네트워크에 연결되어 있음

**해결:**
```bash
# 모든 서비스 중지 및 네트워크 제거
docker-compose down

# 서비스 재시작
docker-compose up -d
```

**전체 초기화 (필요시):**
```bash
# 볼륨까지 모두 삭제
docker-compose down -v

# 클린 재시작
docker-compose up -d
```

---

## 최종 서비스 포트 구성

| 서비스 | 호스트 포트 | 컨테이너 포트 | 접속 URL |
|--------|------------|--------------|----------|
| FastAPI Backend | 8001 | 8000 | http://localhost:8001 |
| DynamoDB Local | 8000 | 8000 | http://localhost:8000 |
| LocalStack | 14566 | 4566 | http://localhost:14566 |
| PostgreSQL | 5432 | 5432 | localhost:5432 |
| Redis | 6379 | 6379 | localhost:6379 |
| MailHog Web UI | 8025 | 8025 | http://localhost:8025 |
| MailHog SMTP | 1025 | 1025 | localhost:1025 |

---

## 유용한 명령어

### 서비스 상태 확인
```bash
docker-compose ps
```

### 특정 서비스 로그 확인
```bash
docker logs dailydevq-backend
docker logs dailydevq-localstack
docker logs dailydevq-dynamodb
```

### 서비스 재시작
```bash
# 특정 서비스만
docker-compose restart backend

# 전체 재시작
docker-compose restart
```

### 볼륨 포함 완전 초기화
```bash
docker-compose down -v
docker-compose up -d --build
```

### 네트워크 확인
```bash
docker network ls
docker network inspect dailydevq-shared
```

---

## 추가 팁

### Windows/WSL2 환경
- 포트 충돌 발생 시 높은 번호 포트 사용 (10000+)
- Docker Desktop 재시작으로 해결되는 경우도 있음
- `netsh interface ipv4 show excludedportrange protocol=tcp` 로 예약 포트 확인

### LocalStack 디버깅
```bash
# LocalStack 로그 레벨 증가
LOCALSTACK_DEBUG=1 docker-compose up localstack
```

### DynamoDB Local 테이블 확인
```bash
# AWS CLI로 로컬 DynamoDB 접속
aws dynamodb list-tables \
  --endpoint-url http://localhost:8000 \
  --region ap-northeast-2
```

### Backend API 문서
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc
- Health Check: http://localhost:8001/health
