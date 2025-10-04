# AWS 비용 예상 (월간)

## 🎯 DailyDevQ 백엔드 인프라 비용 분석

### 현재 상황
- ✅ **프론트엔드**: Vercel 호스팅 (무료 또는 Pro $20/월)
- ❓ **백엔드**: AWS ECS로 배포 예정

---

## 💰 AWS ECS 비용 계산

### 옵션 1: ECS Fargate (서버리스) ⭐ 추천

**장점:**
- 서버 관리 불필요
- 자동 스케일링
- 사용한 만큼만 과금

**비용 구성:**

#### 1. ECS Fargate 컴퓨팅 비용
**최소 스펙 (0.25 vCPU, 0.5GB RAM):**
- vCPU: $0.04656 per vCPU per hour
- Memory: $0.00511 per GB per hour

```
월간 비용 = (0.25 * $0.04656 + 0.5 * $0.00511) * 730시간
         = ($0.01164 + $0.002555) * 730
         = $0.014195 * 730
         = $10.36/월
```

**권장 스펙 (0.5 vCPU, 1GB RAM):**
```
월간 비용 = (0.5 * $0.04656 + 1.0 * $0.00511) * 730
         = ($0.02328 + $0.00511) * 730
         = $0.02839 * 730
         = $20.72/월
```

#### 2. Application Load Balancer (ALB)
- 시간당 요금: $0.0243/시간
- LCU (Load Balancer Capacity Units): $0.008/LCU-hour
  - 신규 연결: 25/초 = 1 LCU
  - 활성 연결: 3000개 = 1 LCU
  - 처리 데이터: 1GB/시간 = 1 LCU

```
ALB 고정 비용 = $0.0243 * 730시간 = $17.74/월

LCU 비용 (트래픽 적음 가정):
- 신규 연결: 10/초 → 0.4 LCU
- 활성 연결: 1000개 → 0.33 LCU
- 데이터: 10GB/일 → 0.4 LCU
→ 최대 0.4 LCU

LCU 비용 = 0.4 * $0.008 * 730 = $2.34/월

총 ALB 비용 = $17.74 + $2.34 = $20.08/월
```

#### 3. DynamoDB
- **온디맨드 모드** (현재 설정):
  - Write: $1.25 per million writes
  - Read: $0.25 per million reads
  - Storage: $0.25 per GB

```
예상 사용량 (초기):
- 구독 요청: 100/일 → 3000/월
- 읽기: 500/일 → 15,000/월
- 저장 용량: 0.1GB

비용:
- Write: 0.003 * $1.25 = $0.004
- Read: 0.015 * $0.25 = $0.004
- Storage: 0.1 * $0.25 = $0.025

총 DynamoDB 비용 = $0.03/월 (거의 무료)
```

#### 4. ECR (Docker 이미지 저장소)
- Storage: $0.10 per GB/month
- 이미지 크기: ~500MB

```
ECR 비용 = 0.5GB * $0.10 = $0.05/월
```

#### 5. 데이터 전송 (Outbound)
- 첫 1GB: 무료
- 1GB - 10TB: $0.126 per GB

```
예상 트래픽: 10GB/월
비용 = (10 - 1) * $0.126 = $1.13/월
```

---

### 📊 **옵션 1 총 비용 요약 (Fargate)**

| 항목 | 스펙 | 월 비용 |
|------|------|---------|
| ECS Fargate | 0.5 vCPU, 1GB RAM | $20.72 |
| ALB | 기본 + 0.4 LCU | $20.08 |
| DynamoDB | On-Demand | $0.03 |
| ECR | 500MB 이미지 | $0.05 |
| Data Transfer | 10GB/월 | $1.13 |
| **합계** | | **$42.01/월** |

**트래픽 증가 시 (100GB/월):**
- Data Transfer: $11.61
- **총 비용: ~$52.50/월**

---

### 옵션 2: ECS on EC2 (비용 절감)

**장점:**
- Fargate보다 저렴
- Reserved Instance 사용 시 추가 절감

**단점:**
- 서버 관리 필요
- 스케일링 복잡

#### EC2 t3.small (2 vCPU, 2GB RAM)
- On-Demand: $0.0238/시간
- 1년 Reserved (부분 선결제): $0.0144/시간

```
EC2 비용:
- On-Demand: $0.0238 * 730 = $17.37/월
- Reserved (1년): $0.0144 * 730 = $10.51/월 (+ 선불 $50)
```

### 📊 **옵션 2 총 비용 요약 (EC2)**

| 항목 | 스펙 | 월 비용 |
|------|------|---------|
| EC2 | t3.small (On-Demand) | $17.37 |
| ALB | 기본 + 0.4 LCU | $20.08 |
| DynamoDB | On-Demand | $0.03 |
| Data Transfer | 10GB/월 | $1.13 |
| **합계** | | **$38.61/월** |

**Reserved Instance 사용 시: ~$32/월**

---

### 옵션 3: EC2 단독 (ALB 없음) - 최저 비용

**구성:**
- EC2 t3.micro (1 vCPU, 1GB RAM)
- Nginx로 SSL 처리
- Let's Encrypt 무료 인증서

```
비용:
- EC2 t3.micro: $0.012/시간 * 730 = $8.76/월
- DynamoDB: $0.03/월
- Data Transfer: $1.13/월

총 비용 = $9.92/월
```

**주의:**
- 단일 장애점 (HA 없음)
- 수동 스케일링 필요
- SSL 관리 직접 필요

---

## 💡 비용 절감 방법

### 1. AWS 프리티어 활용 (12개월)
- EC2 t2.micro/t3.micro: 750시간/월 무료
- ALB: 750시간/월 + 15 LCU/월 무료
- Data Transfer: 첫 15GB/월 무료
- DynamoDB: 25GB 저장 + 충분한 읽기/쓰기 무료

**프리티어 사용 시 첫 1년: ~$0 - $5/월**

### 2. Reserved Instance
- 1년 약정: 30-40% 절감
- 3년 약정: 최대 60% 절감

### 3. Spot Instance (개발/테스트)
- EC2 비용 최대 90% 절감
- 프로덕션에는 비추천

### 4. Auto Scaling
- 야간/주말 자동 스케일 다운
- 트래픽 없을 때 인스턴스 0개로 축소

### 5. CloudFront 캐싱
- API 응답 캐싱으로 백엔드 부하 감소
- 데이터 전송 비용 절감

---

## 🎯 추천 구성 (단계별)

### Phase 1: MVP/초기 (프리티어)
- **프론트엔드**: Vercel 무료
- **백엔드**: EC2 t3.micro (프리티어)
- **DB**: DynamoDB (프리티어)
- **월 비용**: **$0 - $5**

### Phase 2: 성장기 (트래픽 증가)
- **프론트엔드**: Vercel Pro ($20/월)
- **백엔드**: ECS Fargate 0.5 vCPU, 1GB RAM
- **ALB**: Application Load Balancer
- **월 비용**: **$42 - $60**

### Phase 3: 스케일 (고트래픽)
- **백엔드**: ECS Fargate 1 vCPU, 2GB RAM (Auto Scaling)
- **CDN**: CloudFront
- **캐시**: ElastiCache Redis
- **월 비용**: **$100 - $200**

---

## 📌 결론

### DailyDevQ 서비스 초기 단계

**최저 비용 (프리티어):**
```
EC2 t3.micro (프리티어) + DynamoDB + Vercel = ~$0/월
→ 첫 12개월 무료
```

**안정적 운영 (프리티어 이후):**
```
Option A: EC2 + ALB = ~$38/월
Option B: Fargate + ALB = ~$42/월 ⭐
```

**권장:**
1. **지금**: EC2 t3.micro (프리티어) 사용 → **무료**
2. **프리티어 종료 후**: Fargate로 이전 → **$42/월**
3. **트래픽 증가 시**: Auto Scaling 설정 → **$50-100/월**

---

## ⚠️ 비용 모니터링

**반드시 설정할 것:**
1. AWS Budget 설정 ($50/월 알림)
2. CloudWatch 비용 알람
3. 월간 비용 리포트 확인

**비용 초과 방지:**
```bash
# AWS CLI로 현재 비용 확인
aws ce get-cost-and-usage \
  --time-period Start=2025-10-01,End=2025-10-31 \
  --granularity MONTHLY \
  --metrics BlendedCost
```
