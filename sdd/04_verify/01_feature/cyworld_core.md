# 검증 요약: 싸이월드 핵심 슬라이스 (retained)

> 04_verify: command-level 증거 기준. 추정 금지.

## 게이트 결과

- 명령: `python proof/run_proof.py` → **exit 0**
- 결과: **25/25 PASS** (`tmp/proof-results.json`, gate=pytest, status=PASS)
- 명령: `python -m pytest -q` → `25 passed`

## EARS AC ↔ 테스트 매핑 (전부 PASS)

| 도메인 | AC | 테스트 |
| --- | --- | --- |
| 미니홈피 | HOME AC-1~AC-5 | `tests/test_minihome.py` (5) |
| 미니홈피 | HOME AC-6(화면) | `tests/test_screen_parity.py` (2) |
| 일촌 | ILCHON AC-1~AC-6 | `tests/test_ilchon.py` (6) |
| 도토리 | ACORN AC-1~AC-6 | `tests/test_acorn.py` (6) |
| 방명록 | GUEST AC-1~AC-4 | `tests/test_guestbook.py` (4) |
| 회귀(공유) | — | `tests/test_regression.py` (2) |

## 불변식 검증

- 도토리 `balance == sum(ledger)`: `test_acorn.py::test_balance_equals_ledger_sum` PASS.
- 일촌 양방향 정합(맺기·해제 동시): `test_ilchon.py::test_accept_creates_mutual`,
  `test_break_removes_both_directions` PASS.
- 미니홈피 본인 방문 제외: `test_minihome.py::test_owner_visit_not_counted` PASS.

## 회귀 범위 (선정)

- direct: 미니홈피·일촌·도토리·방명록 4개 도메인 테스트.
- shared: `shared/visibility.py`·`shared/idem.py` 계약 회귀(`test_regression.py`).
- 근거: `sdd/02_plan/10_test/regression_verification.md`.

## 잔여 리스크

- 저장이 인메모리라 동시성/영속성은 미검증 — RDB 이행 시 트랜잭션·락 검증 필요.
- 화면 parity는 결정적 HTML 스냅샷 대용(브라우저 비가용). 실 픽셀 exactness는 미적용.
- 배포(05_operate)는 범위 밖 — 본 작업은 구현·검증까지. 롤아웃 미수행.
