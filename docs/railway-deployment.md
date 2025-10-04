# Railway 배포 가이드

## 🚂 Railway란?

- Vercel의 백엔드 버전
- GitHub 연동으로 자동 배포
- Python/FastAPI 완벽 지원
- 무료 크레딧: $5/월

## 📦 사전 준비

1. **Railway 계정 생성**
   - https://railway.app 접속
   - GitHub 계정으로 로그인

2. **환경변수 준비**
   - `.env.production` 파일 내용 복사

---

## 🚀 배포 방법

### 방법 1: Railway Dashboard (웹)

1. **New Project 클릭**
   - "Deploy from GitHub repo" 선택
   - `dailydevq-backend` 레포지토리 선택

2. **환경변수 설정**
   - Settings → Variables 탭
   - `.env.production` 내용 하나씩 추가:
   ```
   AWS_ACCESS_KEY_ID=your-key
   AWS_SECRET_ACCESS_KEY=your-secret
   AWS_REGION=ap-northeast-2
   DYNAMODB_ENDPOINT=  (비워두기)
   DYNAMODB_TABLE_PREFIX=dailydevq-prod
   DYNAMODB_USERS_TABLE=Users
   JWT_SECRET=your-strong-secret
   GOOGLE_CLIENT_ID=your-client-id
   GOOGLE_CLIENT_SECRET=your-client-secret
   CORS_ORIGINS=https://dailydevq.com,https://www.dailydevq.com
   ```

3. **배포 확인**
   - Deployments 탭에서 진행 상황 확인
   - 성공 시 URL 제공: `https://dailydevq-backend-production.up.railway.app`

4. **커스텀 도메인 설정** (선택)
   - Settings → Domains
   - `api.dailydevq.com` 추가
   - DNS에 CNAME 레코드 추가

---

### 방법 2: Railway CLI

```bash
# 1. Railway CLI 설치
npm i -g @railway/cli

# 2. 로그인
railway login

# 3. 프로젝트 초기화
cd /home/sdhcokr/project/dailydevq-backend
railway init

# 4. 환경변수 설정
railway variables set AWS_ACCESS_KEY_ID=your-key
railway variables set AWS_SECRET_ACCESS_KEY=your-secret
railway variables set AWS_REGION=ap-northeast-2
railway variables set DYNAMODB_ENDPOINT=
railway variables set JWT_SECRET=your-secret
railway variables set GOOGLE_CLIENT_ID=your-client-id
railway variables set GOOGLE_CLIENT_SECRET=your-client-secret
railway variables set CORS_ORIGINS=https://dailydevq.com

# 5. 배포
railway up

# 6. 로그 확인
railway logs

# 7. 도메인 확인
railway domain
```

---

## 🔧 설정 파일

Railway는 다음 파일들을 자동으로 인식합니다:

### 1. `railway.json` (Railway 설정)
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn dailydevq_backend.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

### 2. `nixpacks.toml` (빌드 설정)
```toml
[phases.setup]
nixPkgs = ["python312", "curl"]

[phases.install]
cmds = ["pip install uv", "uv pip install --system -e ."]

[start]
cmd = "uvicorn dailydevq_backend.main:app --host 0.0.0.0 --port $PORT"
```

### 3. `Procfile` (프로세스 정의)
```
web: uvicorn dailydevq_backend.main:app --host 0.0.0.0 --port $PORT
```

---

## ✅ 배포 체크리스트

**배포 전:**
- [ ] AWS DynamoDB 테이블 생성 확인
- [ ] Google OAuth 리디렉션 URI 추가
- [ ] `.env.production` 환경변수 준비
- [ ] GitHub 레포지토리 푸시

**배포 후:**
- [ ] Health Check 확인: `https://your-app.up.railway.app/health`
- [ ] API 문서 확인: `https://your-app.up.railway.app/docs`
- [ ] 구독 테스트
- [ ] Google OAuth 테스트
- [ ] DynamoDB 데이터 저장 확인

---

## 🔗 프론트엔드 연동

**Vercel 환경변수 업데이트:**

```bash
# Vercel Dashboard → Settings → Environment Variables
NEXT_PUBLIC_API_URL=https://your-app.up.railway.app

# 또는 커스텀 도메인 사용 시
NEXT_PUBLIC_API_URL=https://api.dailydevq.com
```

**재배포:**
```bash
cd /home/sdhcokr/project/dailydevq-app
vercel --prod
```

---

## 💰 비용 관리

### 무료 크레딧
- $5/월 제공
- 500MB RAM 기준 약 150시간 실행 가능

### 사용량 확인
```bash
railway usage
```

### 비용 절감 팁
1. **Autoscaling 비활성화** (초기에는 1개 인스턴스로 충분)
2. **Sleep on Idle** (트래픽 없을 때 자동 중지)
3. **로그 레벨 조정** (불필요한 로그 최소화)

---

## 🐛 트러블슈팅

### 1. 빌드 실패
```bash
# 로그 확인
railway logs --deployment

# 일반적인 원인:
# - pyproject.toml 경로 오류
# - Python 버전 불일치
# - 의존성 설치 실패
```

### 2. 런타임 에러
```bash
# 환경변수 확인
railway variables

# 누락된 환경변수 추가
railway variables set KEY=value
```

### 3. DynamoDB 연결 실패
- `DYNAMODB_ENDPOINT`가 비어있는지 확인 (프로덕션에서는 비워야 함)
- AWS 자격증명 확인
- IAM 권한 확인

### 4. CORS 에러
- `CORS_ORIGINS`에 프론트엔드 도메인 정확히 입력
- `https://` 포함 여부 확인
- 백엔드 재배포

---

## 📊 모니터링

### Railway Dashboard
- Metrics → CPU, Memory, Network 사용량 확인
- Logs → 실시간 로그 모니터링
- Deployments → 배포 히스토리

### 알림 설정
- Settings → Notifications
- Slack/Discord 웹훅 연동

---

## 🔄 자동 배포 (CI/CD)

Railway는 GitHub 연동 시 자동으로 CI/CD가 설정됩니다:

1. `main` 브랜치에 푸시
2. Railway가 자동으로 빌드 & 배포
3. Health Check 통과 시 트래픽 전환

**수동 배포 트리거:**
```bash
railway up --detach
```

---

## 📝 다음 단계

1. **Railway 배포 완료 후:**
   - [ ] API URL 복사
   - [ ] Vercel 환경변수 업데이트
   - [ ] 프론트엔드 재배포

2. **커스텀 도메인 설정:**
   - [ ] `api.dailydevq.com` DNS 설정
   - [ ] Railway에 도메인 추가
   - [ ] SSL 자동 활성화

3. **모니터링 설정:**
   - [ ] Railway 알림 설정
   - [ ] AWS CloudWatch (DynamoDB)
   - [ ] Sentry 에러 트래킹 (선택)
