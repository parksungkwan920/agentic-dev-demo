# 검증 요약: 사진첩 (retained)

> 04_verify: command-level 증거 기준. 추정 금지.

## 게이트 결과

- 명령: `python proof/run_proof.py` → **exit 0**
- 결과: **31/31 PASS** (기존 25 + 사진첩 5 + scope 회귀 1) — `tmp/proof-results.json`

## EARS AC ↔ 테스트 매핑 (전부 PASS)

| AC | 테스트 |
| --- | --- |
| PHOTO AC-1 업로드 권한 | `test_photo.py::test_upload_owner_only` |
| PHOTO AC-2 공개범위 필터 | `test_photo.py::test_scope_visibility` |
| PHOTO AC-3 대표사진 1장·권한 | `test_photo.py::test_cover_single_and_owner_only` |
| PHOTO AC-4 삭제 권한·대표 해제 | `test_photo.py::test_delete_owner_only_and_clears_cover` |
| PHOTO AC-5 미니홈피 연동 | `test_photo.py::test_minihome_photo_summary` |
| 회귀 scope 계약 | `test_regression.py::test_scope_contract` |

## 회귀 범위 (선정)

- direct: 사진첩(`test_photo.py`).
- shared: `shared/visibility.can_see_scope` 추가 → 기존 `test_regression.py` 전체 + 미니홈피
  연동(`test_minihome.py`)이 함께 green인지 확인. 25→31 전수 통과로 비파괴 확인.

## 잔여 리스크

- 사진 바이너리/스토리지는 미구현(데모는 caption + scope 메타데이터만). 실제 업로드·썸네일은 범위 밖.
- 갤러리·게시판·쪽지함·BGM은 여전히 deferred(화면 placeholder).
- 배포(05_operate)는 범위 밖 — 롤아웃 미수행.
