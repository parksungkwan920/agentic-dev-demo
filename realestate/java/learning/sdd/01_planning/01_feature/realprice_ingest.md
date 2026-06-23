# 실거래가 수집·집계 · Acceptance Criteria (EARS)

> 출처: `00_sources/02_requirements/realfield-부동산실거래.md` (원문 요구 1~5 → AC-1~AC-5)  
> 함께 참조: `00_sources/01_apis/molit_apt_trade_api.md`, `00_sources/03_data_spec/realprice_data_spec.md`  
> 각 AC는 통과/실패를 판정할 수 있는 검증 가능한 명세입니다. 구현 에이전트는 이 다섯 줄을 벗어날 수 없습니다.

AC-1  When 특정 시군구(LAWD_CD)·계약월(DEAL_YMD)로 수집을 요청하면,
      the system shall data.go.kr 아파트 매매 실거래가 API를 호출해
      결과를 표준 스키마(AptTransaction)로 정규화하고 거래원장에 적재한다.

AC-2  When data.go.kr 응답이 지연되거나 실패하면,
      the system shall 재시도 3회 → 서킷브레이커 → 빈 결과(부분 수집)로
      우아하게 저하한다. 외부 장애가 파이프라인 전체를 멈추지 않는다. (회복력)

AC-3  The 거래금액 파싱은 shall 콤마·공백 포함 만원 문자열(" 82,500")을
      원 단위 정수(825,000,000)로 변환하고,
      해제된 거래(cdealType = O)는 시세 집계에서 제외한다. (데이터 정합)
      - 콤마 금액 변환: 공백·콤마 제거 → 만원 정수 → ×10,000 = 원 단위 (DAR-002, CONR-003)
      - 해제거래 제외: cdealType = "O" → canceled=true → 시세 집계 대상 제외 (SFR-006, DAR-004)
      - 해제 거래는 원장에 유지, 집계에서만 논리적 제외 (DAR-005)

AC-4  When 동일 (시군구·계약월) 수집이 재실행되면,
      the system shall 자연키 기반 멱등 upsert로 중복 거래를 만들지 않는다.

AC-5  When 시세 통계를 조회하면,
      the system shall 거래원장(write model)이 아니라 analytics read model에서
      중위 거래금액·중위 ㎡당 단가를 반환한다. (CQRS 읽기 분리)

AC-R  회귀: 게이트웨이 라우팅·디스커버리 등록·기존 조회 API 계약이 무손상이어야 한다.

---

## 요구사항 → AC 추적

| 요구사항 ID | 명칭 | 수용기준 |
| --- | --- | --- |
| SFR-001 | 실거래 수집 요청 | AC-1 |
| SFR-002 | 페이징 전량 수집 | AC-1 |
| SFR-003 | 표준 스키마 정규화 | AC-1 |
| SFR-004 | 거래금액 정규화 (콤마 금액 변환) | **AC-3** |
| SFR-005 | 멱등 적재 | AC-4 |
| SFR-006 | 해제 거래 처리 (해제거래 제외) | **AC-3** |
| SFR-008 / SFR-009 | 시세 통계 조회 / CQRS 분리 | AC-5 |
| SFR-011 | 부분 수집 허용 | AC-2 |
| SFR-013 | 재수집/백필 | AC-4 |
| DAR-002 | 금액 정규화 규칙 | **AC-3 (콤마 금액 변환)** |
| DAR-004 | 해제 플래그 | **AC-3 (해제거래 제외)** |
| SIR-005 | 연계 회복력 | AC-2 |
