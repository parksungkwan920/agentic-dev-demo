# 다이어리 · todos + 실행 계획

## Scope
미니홈피 다이어리 한 도메인을 작성·공개범위·조회·삭제 + 미니홈피 연동까지 구현·검증.
deferred였던 항목을 실제 구현으로 승격(기존 비공개 섹션 플래그를 실제 글 CRUD로 채움).

## Acceptance Criteria
- DIARY AC-1~AC-4 (`sdd/01_planning/01_feature/diary_feature_spec.md`) 전부 테스트 통과.
- 공개범위는 사진첩과 같은 `shared/visibility.can_see_scope` 재사용, 회귀 green.

## Feature Items
| Code       | Use Case                          | Status | Notes |
| ---------- | --------------------------------- | ------ | ----- |
| DIARY-F001 | 작성(주인)·공개범위 필터·조회      | done   | public/ilchon/private |
| DIARY-F002 | 삭제(주인)                         | done   |       |
| DIARY-F003 | 미니홈피 연동(섹션 비공개 + 글 수) | done   | 섹션 가려지면 0 |

## Execution Checklist (비중첩)
- [x] T1 @backend-dev  다이어리 도메인 (`server/contexts/diary/diary.py`)
- [x] T2 @backend-dev  미니홈피 연동 (`server/contexts/minihome/minihome.py`)
- [x] T3 @test-dev     test_diary (`tests/test_diary.py`)
- [x] T4 @frontend-dev 데모 화면 다이어리 실값 (`sdd/99_toolchain/01_automation/render_minihome_demo.py`)

## Regression Scope
- direct: 다이어리 흐름(`test_diary.py`)
- shared: `shared/visibility.can_see_scope`(사진첩과 공유) → 사진첩·미니홈피 회귀 재확인
- 근거: `sdd/02_plan/10_test/regression_verification.md`

## Validation
- `python proof/run_proof.py` → exit 0, 36/36 PASS (`tmp/proof-results.json`).
