# 다이어리 · Acceptance Criteria (EARS)

> 01_planning: 요구사항을 검증 가능한 EARS로 정제. 이 명세가 가드레일.
> 도메인 코드: DIARY · 공개범위(scope)는 shared/visibility 규칙을 재사용한다.

**AC-1** When 홈피 주인이 다이어리를 작성하면, the system shall (owner, title, body, mood,
scope, 시각) 글을 저장한다. Where 작성자가 홈피 주인이 아니면 작성을 거부한다.

**AC-2** Where 글의 공개범위가 ilchon이고 조회자가 일촌이 아니거나, public이 아닌 private이고
조회자가 주인이 아니면, the system shall 그 글을 목록·조회에서 제외한다.
(public은 누구에게나 노출)

**AC-3** When 주인이 다이어리를 삭제하면, the system shall 글을 제거한다. Where 삭제자가
주인이 아니면 거부한다.

**AC-4(연동)** The 미니홈피 메인은 shall 조회자에게 보이는(공개범위 통과) 다이어리 글 수를
노출하되, 다이어리 섹션이 비공개로 가려지는 조회자(타인)에게는 0으로 노출한다.

## 검증 매핑

| AC | 테스트 |
| --- | --- |
| AC-1 | `tests/test_diary.py::test_write_owner_only` |
| AC-2 | `tests/test_diary.py::test_scope_visibility` |
| AC-3 | `tests/test_diary.py::test_delete_owner_only` |
| AC-4 | `tests/test_diary.py::test_minihome_diary_count` |
| 회귀 | `tests/test_regression.py` (visibility scope 계약) |
