# 검증 요약: 다이어리 (retained)

> 04_verify: command-level 증거 기준. 추정 금지.

## 게이트 결과

- 명령: `python proof/run_proof.py` → **exit 0**
- 결과: **36/36 PASS** (기존 31 + 다이어리 5) — `tmp/proof-results.json`

## EARS AC ↔ 테스트 매핑 (전부 PASS)

| AC | 테스트 |
| --- | --- |
| DIARY AC-1 작성 권한 | `test_diary.py::test_write_owner_only` |
| DIARY AC-2 공개범위 필터 | `test_diary.py::test_scope_visibility` |
| DIARY AC-3 삭제 권한 | `test_diary.py::test_delete_owner_only` |
| DIARY AC-4 미니홈피 연동(섹션 비공개) | `test_diary.py::test_minihome_diary_count` |
| DIARY AC-4 연동(섹션 공개+글별 scope) | `test_diary.py::test_minihome_diary_count_public_section` |

## 회귀 범위 (선정)

- direct: 다이어리(`test_diary.py`).
- shared: `can_see_scope`는 사진첩과 공유 — 31→36 전수 통과로 비파괴 확인.

## 잔여 리스크

- 다이어리 본문은 plain text(에디터·이미지 첨부 없음). 댓글/방명록형 상호작용 미구현.
- 갤러리·게시판·쪽지함·BGM은 여전히 deferred(화면 placeholder).
- 배포(05_operate)는 범위 밖 — 롤아웃 미수행.
