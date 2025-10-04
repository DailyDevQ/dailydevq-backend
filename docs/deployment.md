# 프로덕션 배포 가이드

## 📋 사전 준비사항

### 1. AWS 인프라
- [x] DynamoDB 테이블 생성 완료 (`Users`)
- [ ] S3 버킷 생성 (정적 파일, 이미지 등)
- [ ] SES 설정 (이메일 발송)
- [ ] RDS PostgreSQL (선택사항)
- [ ] ElastiCache Redis (선택사항)
- [ ] ECR (Docker 이미지 저장소)
- [ ] ECS/Fargate 또는 EC2

### 2. 도메인 및 SSL
- [ ] 도메인 구입 및 DNS 설정
  - `dailydevq.com` - 프론트엔드
  - `api.dailydevq.com` - 백엔드 API
- [ ] SSL 인증서 발급 (AWS Certificate Manager 또는 Let's Encrypt)

### 3. 외부 서비스
- [x] Google OAuth 설정 (프로덕션 리디렉션 URI 추가)
- [ ] OpenAI API 키 (선택사항)
- [ ] Anthropic API 키 (선택사항)

---

## 🚀 백엔드 배포

### 1. 환경변수 설정

`.env.production` 파일 생성:

```bash
cp .env.production.example .env.production
```

필수 환경변수 입력:
- `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`
- `JWT_SECRET` (강력한 랜덤 문자열, 최소 32자)
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET`
- `DYNAMODB_ENDPOINT` (비워두면 실제 AWS DynamoDB 사용)
- `CORS_ORIGINS` (프론트엔드 도메인)

### 2. Docker 이미지 빌드

```bash
# 프로덕션 이미지 빌드
docker build -t dailydevq-backend:latest -f Dockerfile .

# 테스트 실행
docker run --rm -p 8000:8000 --env-file .env.production dailydevq-backend:latest
```

### 3. AWS ECR에 푸시

```bash
# ECR 로그인
aws ecr get-login-password --region ap-northeast-2 | docker login --username AWS --password-stdin <AWS_ACCOUNT_ID>.dkr.ecr.ap-northeast-2.amazonaws.com

# 이미지 태그
docker tag dailydevq-backend:latest <AWS_ACCOUNT_ID>.dkr.ecr.ap-northeast-2.amazonaws.com/dailydevq-backend:latest

# 푸시
docker push <AWS_ACCOUNT_ID>.dkr.ecr.ap-northeast-2.amazonaws.com/dailydevq-backend:latest
```

### 4. ECS/Fargate 배포

Task Definition 생성:
- 이미지: ECR 이미지 URI
- 환경변수: `.env.production` 내용을 ECS 환경변수 또는 Secrets Manager로 관리
- 포트 매핑: 8000
- Health Check: `/health`

Service 생성:
- Load Balancer 연결 (ALB)
- Target Group: Health check path `/health`
- Auto Scaling 설정

---

## 🎨 프론트엔드 배포 (Vercel 권장)

### 1. Vercel 배포

```bash
cd /home/sdhcokr/project/dailydevq-app

# Vercel CLI 설치
npm i -g vercel

# 로그인
vercel login

# 배포
vercel --prod
```

### 2. 환경변수 설정 (Vercel Dashboard)

프로젝트 Settings → Environment Variables:
- `NEXT_PUBLIC_API_URL=https://api.dailydevq.com`
- `NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-client-id`
- `NEXTAUTH_SECRET=your-secret`
- `NEXTAUTH_URL=https://dailydevq.com`

### 3. 커스텀 도메인 설정

Vercel Dashboard → Domains:
- `dailydevq.com` 추가
- DNS 레코드 설정 (Vercel에서 제공하는 CNAME)

---

## 🔧 대안: Self-Hosted 배포

### Next.js Static Export + S3 + CloudFront

```bash
# 1. Next.js 빌드
cd /home/sdhcokr/project/dailydevq-app
pnpm build

# 2. S3 버킷에 업로드
aws s3 sync out/ s3://dailydevq-frontend-bucket/ --delete

# 3. CloudFront 캐시 무효화
aws cloudfront create-invalidation --distribution-id YOUR_DISTRIBUTION_ID --paths "/*"
```

---

## 🔐 보안 체크리스트

- [ ] `.env.production` 파일은 Git에 커밋하지 않음 (`.gitignore`에 추가)
- [ ] JWT_SECRET은 강력한 랜덤 문자열 사용
- [ ] AWS IAM 최소 권한 원칙 적용
- [ ] CORS 설정에 실제 프론트엔드 도메인만 허용
- [ ] API 문서 비활성화 (`ENABLE_SWAGGER=false`)
- [ ] HTTPS 강제 적용
- [ ] Rate Limiting 설정 (API Gateway 또는 애플리케이션 레벨)

---

## 📊 모니터링

### CloudWatch 설정
- ECS 로그 그룹
- 메트릭: CPU, 메모리, 요청 수
- 알람: 에러율, 응답 시간

### 헬스체크
- ALB Health Check: `/health`
- ECS Health Check: 30초 간격

---

## 🔄 CI/CD 설정 (선택사항)

GitHub Actions 워크플로우:

```yaml
# .github/workflows/deploy-backend.yml
name: Deploy Backend

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ap-northeast-2

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1

      - name: Build, tag, and push image to Amazon ECR
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: dailydevq-backend
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG

      - name: Update ECS service
        run: |
          aws ecs update-service --cluster dailydevq-cluster --service dailydevq-backend --force-new-deployment
```

---

## 📝 배포 후 체크리스트

- [ ] API 엔드포인트 정상 작동 확인 (`https://api.dailydevq.com/health`)
- [ ] 프론트엔드 정상 로드 확인 (`https://dailydevq.com`)
- [ ] Google OAuth 로그인 테스트
- [ ] 이메일 구독 테스트
- [ ] DynamoDB 데이터 저장 확인
- [ ] 로그 확인 (CloudWatch)
- [ ] SSL 인증서 확인
- [ ] 모니터링 대시보드 설정

---

## 🆘 트러블슈팅

### CORS 에러
- 백엔드 `CORS_ORIGINS` 설정 확인
- 프론트엔드 도메인이 정확히 일치하는지 확인

### DynamoDB 연결 실패
- IAM 권한 확인
- `DYNAMODB_ENDPOINT`가 비어있는지 확인 (프로덕션에서는 비워둠)
- 테이블 이름 확인 (`Users`)

### Google OAuth 실패
- Google Cloud Console에서 프로덕션 리디렉션 URI 추가 확인
- `https://dailydevq.com/auth/google/callback`

### 이미지 빌드 실패
- Docker 캐시 클리어: `docker builder prune`
- 로그 확인: `docker build --no-cache --progress=plain .`
