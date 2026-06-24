# 사진첩 · todos + 실행 계획

## Scope
미니홈피 사진첩 한 도메인을 업로드·공개범위·대표사진·삭제 + 미니홈피 연동까지 구현·검증.
deferred였던 항목을 실제 구현으로 승격.

## Acceptance Criteria
- PHOTO AC-1~AC-5 (`sdd/01_planning/01_feature/photo_feature_spec.md`) 전부 테스트 통과.
- 공개범위(scope)는 shared/visibility로 일원화, 회귀 green.

## Feature Items
| Code       | Use Case                       | Status | Notes |
| ---------- | ------------------------------ | ------ | ----- |
| PHOTO-F001 | 업로드(주인)·공개범위 필터      | done   | public/ilchon/private |
| PHOTO-F002 | 대표사진(cover)·삭제            | done   | 대표 최대 1장 |
| PHOTO-F003 | 미니홈피 메인 연동(수·대표)     | done   | 조회자 공개범위 반영 |

## Execution Checklist (비중첩)
- [x] T1 @backend-dev  shared/visibility에 can_see_scope 추가 (`server/shared/visibility.py`)
- [x] T2 @backend-dev  사진첩 도메인 (`server/contexts/photo/photo.py`)
- [x] T3 @backend-dev  미니홈피 연동 (`server/contexts/minihome/minihome.py`)
- [x] T4 @test-dev     test_photo + scope 회귀 보강 (`tests/`)
- [x] T5 @frontend-dev 데모 화면 사진첩 반영 (`sdd/99_toolchain/01_automation/render_minihome_demo.py`)

## Regression Scope
- direct: 사진첩 흐름(`test_photo.py`)
- shared: `shared/visibility.py`(can_see_scope 추가) → 사진첩·미니홈피·방명록 회귀(`test_regression.py`)
- 근거: `sdd/02_plan/10_test/regression_verification.md`

## Validation
- `python proof/run_proof.py` → exit 0, 31/31 PASS (`tmp/proof-results.json`).
