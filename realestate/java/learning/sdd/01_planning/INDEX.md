# 01_planning INDEX: RealField

> `00_sources` 요구사항을 구조화한 계획 산출물의 색인입니다.

| 섹션 | 파일 | 내용 |
| --- | --- | --- |
| 01_feature | `01_feature/realprice_ingest.md` | 기능 수용기준 (EARS AC-1~AC-5) · SFR/DAR 추적표 |
| 03_architecture | `03_architecture/realfield_architecture.md` | MSA 경계·런타임·**사람이 판단한 지점** (4개 트레이드오프 + 기각 대안) |
| 04_data | `04_data/realprice_data.md` | 표준 거래 스키마(AptTransaction) · 금액 정규화(DAR-002) · 자연키(DAR-003) · 해제 처리(DAR-004) · MarketStat 집계 규칙(DAR-007) |
| 05_api | `05_api/realprice_api.md` | 게이트웨이 라우팅 3종 · 엔드포인트 계약(요청·응답·상태코드) · 공통 오류 규약 |
| 07_integration | `07_integration/molit_integration.md` | data.go.kr 연계 계약 · 회복력 정책(재시도·서킷) · Rate limit 대응 · 페이징 · 스케줄링 · 장애 격리 |
| 08_nonfunctional | `08_nonfunctional/realprice_nfr.md` | 성능(PER)·회복력·멱등·가용성 + 제약사항(CONR) |
| 09_security | `09_security/realprice_security.md` | 보안 요구사항(SECR-001~005)·인증키 비노출·감사 |

> 진행 순서는 `HANDSON.md`를 따릅니다. 기능·비기능·보안(Stage 1) → 아키텍처·데이터·API·연계(Stage 2) → 플랜(Stage 3).
>
> **Stage 1 게이트**: AC-1~AC-5 판정 가능한 EARS ✓, AC-3에 콤마 금액 변환·해제거래 제외 ✓  
> **Stage 2 게이트**: bounded context MECE·비중첩 ✓, 모듈 경계 결정 근거 남김 ✓, 기각 대안 명시 ✓
