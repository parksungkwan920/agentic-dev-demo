# 즐겨찾기 · Acceptance Criteria (EARS)

> 01_planning: 요구사항을 검증 가능한 EARS로 정제. 이 명세가 가드레일.
> 도메인 코드: FAV · 다른 미니홈피를 북마크(본인 전용).

**AC-1** When 주인이 다른 사용자를 즐겨찾기에 추가하면, the system shall (owner, target)을
추가 순서대로 저장한다.

**AC-2** Where 대상이 자기 자신이거나 이미 즐겨찾기에 있으면, the system shall 추가를
거부한다(중복/자기참조 방지).

**AC-3** When 주인이 즐겨찾기를 삭제하면, the system shall 해당 항목을 제거한다.

**AC-4** The system shall 즐겨찾기 목록을 추가한 순서대로 제공한다.

**AC-5(노출)** The 즐겨찾기는 shall 홈피 주인 본인에게만 노출한다(타인 시점 비공개).

## 검증 매핑

| AC | 테스트 |
| --- | --- |
| AC-1 | `tests/test_favorite.py::test_add` |
| AC-2 | `tests/test_favorite.py::test_no_self_no_duplicate` |
| AC-3 | `tests/test_favorite.py::test_remove` |
| AC-4 | `tests/test_favorite.py::test_list_order` |
| AC-5 | `serve.py` 런타임(주인 시점만 노출) |
| 회귀 | `tests/test_regression.py` (독립 도메인, 공유 표면 없음) |
