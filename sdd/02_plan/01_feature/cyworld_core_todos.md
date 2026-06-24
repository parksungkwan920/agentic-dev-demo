# 싸이월드 핵심 슬라이스 · todos + 실행 계획

## Scope
미니홈피 · 일촌 · 도토리 · 방명록 4개 도메인을 하나의 일관된 슬라이스로 구현·검증한다.
BGM/사진첩/미니룸 아이템샵은 deferred(이번 범위 밖, INDEX 참조).

## Acceptance Criteria
- 각 도메인 EARS AC 전부 테스트 통과:
  - 미니홈피 `01_planning/01_feature/minihome_feature_spec.md` AC-1~AC-6
  - 일촌 `01_planning/01_feature/ilchon_feature_spec.md` AC-1~AC-6
  - 도토리 `01_planning/01_feature/acorn_feature_spec.md` AC-1~AC-6
  - 방명록 `01_planning/01_feature/guestbook_feature_spec.md` AC-1~AC-4
- 핵심 불변식 green: 도토리 `잔액 = sum(ledger)`, 일촌 양방향 정합.
- 회귀(기존 인증/세션) green.
- 미니홈피 메인 UI parity 1/1.

## Feature Items
| Code        | Use Case                         | Status  | Notes |
| ----------- | -------------------------------- | ------- | ----- |
| HOME-F001   | 미니홈피 메인 + 투데이 카운터     | planned | 본인 방문 제외 |
| HOME-F002   | 공개범위(본인/일촌/타인) 조립     | planned | shared/visibility |
| ILCHON-F001 | 일촌 신청/수락(상호)·멱등         | planned | 호칭쌍 필수 |
| ILCHON-F002 | 일촌 해제 · 파도타기              | planned |       |
| ACORN-F001  | 도토리 충전/구매 · 원장           | planned | 멱등 충전 |
| ACORN-F002  | 도토리 선물(원자적, 일촌 한정)    | planned |       |
| GUEST-F001  | 방명록 작성/삭제·권한             | planned |       |
| GUEST-F002  | 비밀글 가시성 · 차단              | planned |       |

## Execution Checklist (비중첩)
- [x] T1 @backend-dev  shared/idem·visibility 공통 (`server/shared/`)
- [x] T2 @backend-dev  도토리 잔액·원장·선물 (`server/contexts/acorn/`)
- [x] T3 @backend-dev  일촌 신청·수락·해제·파도타기 (`server/contexts/ilchon/`)
- [x] T4 @backend-dev  방명록 작성·삭제·비밀글·차단 (`server/contexts/guestbook/`)
- [x] T5 @backend-dev  미니홈피 메인 조립·투데이 카운터 (`server/contexts/minihome/`)
- [x] T6 @frontend-dev 미니홈피 메인 화면 정합 (`sdd/04_verify/10_test/ui_parity/`)
- [x] T7 @test-dev     도메인별 테스트 + 불변식 + UI parity 게이트

## Regression Scope
- direct: 미니홈피·일촌·도토리·방명록 흐름
- shared: `server/shared/idem.py`, `server/shared/visibility.py`, 기존 인증/세션
- 근거: `sdd/02_plan/10_test/regression_verification.md`

## Current Notes
- canonical 기능코드(HOME/ILCHON/ACORN/GUEST) 기준으로만 갱신 (날짜 파일 X).
- 의존 순서: idem/visibility → acorn → ilchon → guestbook → minihome(조립).

## Latest Verification
- proof: `python proof/run_proof.py` → exit 0, 25/25 PASS (`tmp/proof-results.json`).
- 상세: `sdd/04_verify/01_feature/cyworld_core.md`.
