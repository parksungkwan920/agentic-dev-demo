# 실거래가 수집·집계 · 구현 요약 (03_build)

> SDD 'build' 산출물. current-state only — dated execution narrative 금지.

## 구현 범위

- T2(@transaction-dev): 거래원장 write model — 멱등 upsert + 조회 API (AC-4)
- T3(@analytics-dev): 시세 통계 read model — 해제거래 제외·중위값 집계 (AC-5·AC-3)
- T4(@platform-dev): 플랫폼 인프라 — Eureka, Config Server, API Gateway
- @frontend-dev: Next.js 15 + shadcn/ui 3화면 — 수집 트리거·거래 조회·시세 분석

## 변경 모듈

| 모듈 | 상태 | 주요 산출물 |
| --- | --- | --- |
| `common` | ✅ 구현 완료 | `AptTransaction` record · `DealAmountParser` |
| `transaction-service` | ✅ 구현 완료 | 포트·어댑터·서비스·컨트롤러 |
| `analytics-service` | ✅ 구현 완료 | `MarketStat` · `MarketStatCalculator` · 서비스·컨트롤러 |
| `service-discovery` | ✅ 구현 완료 (T4) | `@EnableEurekaServer`, port 8761 |
| `config-server` | ✅ 구현 완료 (T4) | `@EnableConfigServer`, port 8888, native profile |
| `api-gateway` | ✅ 구현 완료 (T4) | port 8080, 3-route `lb://` 라우팅 |
| `web` (Next.js) | ✅ 구현 완료 | `/ingest` · `/transactions` · `/analytics` · `lib/api.ts` · `QueryForm` |
| `ingestion-service` | ⬜ 미구현 (T1) | — |

## 계약·자산

| 항목 | 내용 |
| --- | --- |
| 공유 계약 | `common/AptTransaction` (record, naturalKey() · pricePerSquareMeter() 포함) |
| 정합 규칙 | `common/DealAmountParser.toWon()` — 콤마 만원→원 단위 변환 (AC-3) |
| 포트 | `transaction.port.AptTradeStore` — existsByNaturalKey · save · findByRegionMonth |
| 어댑터 | `JpaAptTradeStore` → `AptTradeRepository` (JPA, `uk_apt_trade_natural` 유니크 제약) |
| read model | `analytics.domain.MarketStat` — tradeCount · medianPriceWon · medianPricePerM2Won |
| 집계 로직 | `MarketStatCalculator.calculate()` — canceled=false 필터 → 중위값 계산 |
| API (transaction) | `POST /api/v1/transactions/bulk`, `GET /api/v1/transactions` |
| API (analytics) | `GET /api/v1/market-stats?sggCd=&dealYear=&dealMonth=` |
| 게이트웨이 라우트 | `/api/v1/ingest/**` → `lb://ingestion-service` |
| | `/api/v1/transactions/**` → `lb://transaction-service` |
| | `/api/v1/market-stats/**` → `lb://analytics-service` |
| Config (Resilience4j) | retry max-attempts 3, wait 500ms · CB sliding-window 20, failure 50%, open 10s |
| Config (보안) | `molit.service-key: ${MOLIT_SERVICE_KEY:}` — 환경변수 외부화, 설정 파일 미노출 (SECR-002) |

## 현재 사용자 가시 동작

- `POST /api/v1/transactions/bulk` — 자연키 existsBy 체크 후 신규만 INSERT, 적재 건수 반환 (재전송 시 0, AC-4)
- `GET /api/v1/transactions?sggCd=&dealYear=&dealMonth=` — 시군구·계약월 거래 목록 조회
- `GET /api/v1/market-stats?sggCd=&dealYear=&dealMonth=` — `lb://transaction-service` 조회 → canceled 제외 → 중위값 집계 반환 (AC-5, AC-3)
- 8080 단일 진입점으로 위 모든 API 라우팅 (api-gateway)
- 서비스 등록·디스커버리: Eureka (8761), 설정 배포: Config Server (8888)

## 검증한 회귀 범위

| 테스트 | 검증 AC | 결과 |
| --- | --- | --- |
| `DealAmountParserTest` | AC-3 콤마 금액 변환 | ✅ |
| `IdempotentUpsertTest` | AC-4 재적재 중복 0 | ✅ |
| `MarketStatCalculatorTest` (홀수 중위) | AC-5 중위값 집계 | ✅ |
| `MarketStatCalculatorTest` (해제 제외) | AC-3 해제거래 집계 제외 | ✅ |
| `MarketStatCalculatorTest` (빈 목록) | 경계 케이스 | ✅ |
| `:service-discovery:compileJava` | T4 플랫폼 컴파일 | ✅ |
| `:config-server:compileJava` | T4 플랫폼 컴파일 | ✅ |
| `:api-gateway:compileJava` | T4 플랫폼 컴파일 | ✅ |
| `next build` (타입 체크 포함) | 프론트엔드 정적 빌드 | ✅ |
| `./gradlew test` (전체) | T1 포함 8/8 단위 테스트 | ✅ |
| Playwright E2E (브라우저) | 수집→거래조회→시세분석 1시나리오 | ✅ 1 passed (6.0s) |

> `./gradlew test` 전체 8/8 통과.
> Playwright E2E: stub 프로필(정상 4+해제 1) 기준 결정적 검증 완료.
> - 수집: upserted 5건, 재수집 0건(멱등)
> - 거래조회: 5행, cancel-badge 1개, 해제거래 토글 후 4행
> - 시세분석: tradeCount=4, medianPriceWon=850,000,000원("8억 5,000만원"), 산점도 렌더
