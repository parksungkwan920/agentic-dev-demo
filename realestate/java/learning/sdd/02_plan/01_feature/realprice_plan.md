# 02_plan · 작업 계획

> 3단계 '플랜' 산출물입니다. 모듈 의존·런타임 흐름·proof 게이트를 확정합니다.
> 추적: 03_architecture → 04_data → 05_api → 02_plan.

---

## 모듈 의존 그래프

```
common ──┬─→ ingestion-service ──(WebClient, lb)──→ transaction-service
         ├─→ transaction-service
         └─→ analytics-service ──(WebClient, lb)──→ transaction-service

service-discovery(Eureka) ← 모든 서비스 등록
config-server              ← ingestion 설정·인증키(MOLIT_SERVICE_KEY) 외부화
api-gateway                ← 단일 진입점 (ingest·transactions·market-stats 라우팅)
```

- common은 T1이 소유하며 T2·T3가 단방향으로 의존합니다(역방향 의존 금지).
- transaction-service는 외부(data.go.kr)를 직접 호출하지 않습니다(장애 격리, 아키텍처 판단 2).

---

## 런타임 흐름 (한 기능 end-to-end)

```
POST /api/v1/ingest/apt-trade?lawdCd=11110&dealYmd=202405
  → api-gateway → ingestion-service
      → MolitApiClient.fetchAptTrades  (data.go.kr, 재시도·서킷, AC-2)
      → AptTransactionNormalizer       (DealAmountParser 금액 변환·해제 표시, AC-3)
      → POST lb://transaction-service /api/v1/transactions/bulk  (멱등 upsert, AC-4)

GET /api/v1/market-stats?sggCd=11110&dealYear=2024&dealMonth=5
  → api-gateway → analytics-service
      → GET lb://transaction-service /api/v1/transactions
      → MarketStatCalculator           (해제 제외·중위 집계, AC-3·AC-5)
```

---

## proof 게이트 (02_plan acceptance)

| 테스트 | 검증 AC | 담당 |
| --- | --- | --- |
| `DealAmountParserTest` | AC-3 (콤마 금액 변환) | T1 |
| `AptTransactionNormalizerTest` | AC-1·AC-3 (정규화·해제 표시) | T1 |
| 자연키 멱등 적재 테스트 | AC-4 (재수집 중복 0) | T2 |
| `MarketStatCalculatorTest` | AC-5·AC-3 (중위 집계·해제 제외) | T3 |
| `./gradlew test` exit 0 | 전체 | - |

---

## 병렬 실행 전제 조건

1. common(AptTransaction·DealAmountParser)이 컴파일 가능한 상태여야 T2·T3가 의존할 수 있습니다.
2. T1이 common을 먼저 확정한 뒤 T2·T3 병렬 구현을 시작합니다.
3. T4는 common 의존 없이 독립적으로 진행 가능합니다.
