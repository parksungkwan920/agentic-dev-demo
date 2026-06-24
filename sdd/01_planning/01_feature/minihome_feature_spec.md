# 미니홈피 · Acceptance Criteria (EARS)

> 01_planning: 요구사항을 검증 가능한 EARS로 정제. 이 명세가 가드레일.
> 도메인 코드: HOME

**AC-1** When 방문자가 미니홈피를 열면, the system shall 그 홈피의 투데이(오늘 방문수)를
1 증가시키고 누적 방문수(total)를 함께 갱신한다.

**AC-2** While 미니홈피를 여는 주체가 홈피 주인 본인일 때, the system shall 투데이/누적
방문수를 증가시키지 않는다.

**AC-3** When 미니홈피 메인을 조회하면, the system shall 주인의 미니미/미니룸 식별자,
일촌 수, 최근 방명록 N개를 한 응답에 포함한다.

**AC-4** Where 조회 주체가 홈피 주인 본인이면, the system shall 도토리 잔액을 응답에 포함하고,
타인이면 도토리 잔액을 노출하지 않는다.

**AC-5** Where 섹션이 비공개(예: 다이어리)로 설정되어 있고 조회 주체가 일촌이 아니면,
the system shall 해당 섹션을 응답에서 숨긴다.

**AC-6(화면)** The 미니홈피 메인 화면은 shall 승인된 디자인 스냅샷과 일치한다(UI parity).

## 검증 매핑

| AC | 테스트 |
| --- | --- |
| AC-1 | `tests/test_minihome.py::test_today_increments_on_visit` |
| AC-2 | `tests/test_minihome.py::test_owner_visit_not_counted` |
| AC-3 | `tests/test_minihome.py::test_main_payload_shape` |
| AC-4 | `tests/test_minihome.py::test_acorn_balance_owner_only` |
| AC-5 | `tests/test_minihome.py::test_private_section_hidden_for_non_ilchon` |
| AC-6 | `tests/test_screen_parity.py` + `sdd/99_toolchain/01_automation/run_ui_parity.py` |
| 회귀 | `tests/test_regression.py` |
