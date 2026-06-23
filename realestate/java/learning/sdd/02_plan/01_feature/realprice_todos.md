# 02_plan · 비중첩 작업 분할 (병렬 에이전트)

> 3단계 '플랜' 산출물입니다. 03_architecture의 경계를 따라 작업을 나눕니다.
> 비중첩이 핵심입니다. 모듈이 안 겹쳐야 네 에이전트를 동시에 돌려도 충돌이 없습니다.

---

## T1 @ingestion-dev · data.go.kr 수집 + 정규화 + 회복력 (AC-1·AC-2·AC-3 변환)

담당 모듈: `ingestion-service/`, **`common/`** (소유)

```
[ ] common/AptTransaction         공유 거래 DTO (T2·T3 의존 → 변경 전 합의 필수)
[ ] common/DealAmountParser       콤마 금액 만원→원 변환 (AC-3 정합 규칙 단일 위치)
[ ] MolitApiClient                data.go.kr WebClient 호출 + 전량 페이징
[ ] AptTransactionNormalizer      item → AptTransaction 매핑, canceled 플래그 세팅
[ ] 회복력 설정                    @Retry(3, 0.5s) · @CircuitBreaker(fallback=빈결과)
[ ] IngestionController           POST /api/v1/ingest/apt-trade 수집 트리거
[ ] 단위 테스트                    DealAmountParserTest · AptTransactionNormalizerTest
```

---

## T2 @transaction-dev · 멱등 적재(자연키 upsert) + 조회 API (AC-4)

담당 모듈: `transaction-service/`

```
[ ] AptTradeStore 포트             도메인 포트 인터페이스 (저장·조회)
[ ] JPA 어댑터                     포트 구현체, DB 자연키 유니크 제약
[ ] 멱등 upsert                   자연키 existsBy 체크 → INSERT / UPDATE / no-op
[ ] TransactionController         POST /api/v1/transactions/bulk (내부)
                                  GET  /api/v1/transactions?sggCd&dealYear&dealMonth
[ ] 단위 테스트                    자연키 중복 시 행 수 불변 검증 (AC-4)
```

---

## T3 @analytics-dev · 시세 통계 read model (AC-5·AC-3 해제 제외)

담당 모듈: `analytics-service/`

```
[ ] MarketStatCalculator          canceled=false 필터 → 중위 거래금액·㎡당 단가 집계
[ ] AnalyticsController           GET /api/v1/market-stats?sggCd&dealYear&dealMonth
[ ] transaction-service 조회      lb://transaction-service/api/v1/transactions 호출
[ ] 단위 테스트                    MarketStatCalculatorTest (해제 제외 후 중위값 검증)
```

---

## T4 @platform-dev · 플랫폼 인프라 (AC-R 라우팅)

담당 모듈: `service-discovery/`, `config-server/`, `api-gateway/`

```
[ ] service-discovery             Eureka 등록·발견 (모든 서비스 등록 대상)
[ ] config-server                 MOLIT_SERVICE_KEY 환경변수 외부화 (SECR-001·002)
[ ] api-gateway                   3라우트 라우팅
                                    /api/v1/ingest/**       → ingestion-service
                                    /api/v1/transactions/** → transaction-service
                                    /api/v1/market-stats/** → analytics-service
[ ] 회귀 검증                      게이트웨이 라우팅·디스커버리 등록 무손상 (AC-R)
```

---

## 비중첩 경계 요약 (병렬 안전 확인)

```
T1 → ingestion-service/* · common/*    (MolitApiClient·Normalizer·파서)
T2 → transaction-service/*             (포트/어댑터·멱등 커맨드·JPA)
T3 → analytics-service/*               (MarketStatCalculator·조회)
T4 → service-discovery/* · config-server/* · api-gateway/*
```

모듈 겹침 없음 → 네 에이전트 동시 실행 시 git 충돌 없음.

---

## cross-cutting: common 소유·합의 규칙

| 규칙 | 내용 |
| --- | --- |
| **소유자** | **T1(@ingestion-dev)** |
| 변경 절차 | T1이 PR을 열고, T2·T3가 영향 검토 후 합의(리뷰 승인) |
| 변경 금지 범위 | AptTransaction 필드명·타입, DealAmountParser 반환 타입 변경은 T2·T3 동의 없이 금지 |
| 근거 | 같은 규칙이 수집·원장·분석에 강제되어야 통계 편차가 없음(아키텍처 판단 3) |
