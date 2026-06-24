# 쪽지함 · todos + 실행 계획

## Scope
미니홈피 쪽지함 한 도메인을 1:1 송수신·차단·읽음·집계·삭제 + 미니홈피 연동까지 구현·검증.
deferred였던 항목을 실제 구현으로 승격(화면의 "쪽지함 N/M" 실현).

## Acceptance Criteria
- MSG AC-1~AC-5 (`sdd/01_planning/01_feature/message_feature_spec.md`) 전부 테스트 통과.
- 차단은 방명록과 동일한 blocks 공유, 회귀 green.

## Feature Items
| Code     | Use Case                       | Status | Notes |
| -------- | ------------------------------ | ------ | ----- |
| MSG-F001 | 송수신·차단                     | done   | 차단=방명록 blocks 공유 |
| MSG-F002 | 읽음(수신자 한정)·집계          | done   | unread/total |
| MSG-F003 | 미니홈피 연동(본인 전용 카운트) | done   | 타인 미노출 |

## Execution Checklist (비중첩)
- [x] T1 @backend-dev  쪽지함 도메인 (`server/contexts/message/message.py`)
- [x] T2 @backend-dev  미니홈피 연동 (`server/contexts/minihome/minihome.py`)
- [x] T3 @test-dev     test_message (`tests/test_message.py`)
- [x] T4 @frontend-dev 데모 화면 쪽지함 실값 (`sdd/99_toolchain/01_automation/render_minihome_demo.py`)

## Regression Scope
- direct: 쪽지함 흐름(`test_message.py`)
- shared: blocks(방명록과 공유), 미니홈피 본인 전용 카운트 경로 → 전수 회귀
- 근거: `sdd/02_plan/10_test/regression_verification.md`

## Validation
- `python proof/run_proof.py` → exit 0, 41/41 PASS (`tmp/proof-results.json`).
