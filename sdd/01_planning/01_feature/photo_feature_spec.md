# 사진첩 · Acceptance Criteria (EARS)

> 01_planning: 요구사항을 검증 가능한 EARS로 정제. 이 명세가 가드레일.
> 도메인 코드: PHOTO · 공개범위(scope)는 shared/visibility 규칙을 재사용한다.

**AC-1** When 홈피 주인이 사진을 올리면, the system shall (owner, caption, scope, 시각)
사진을 저장한다. Where 업로더가 홈피 주인이 아니면 업로드를 거부한다.

**AC-2** Where 사진의 공개범위가 ilchon이고 조회자가 일촌이 아니거나, 공개범위가 private이고
조회자가 주인이 아니면, the system shall 그 사진을 목록에서 제외한다. (public은 누구에게나 노출)

**AC-3** When 주인이 대표사진(cover)을 지정하면, the system shall 기존 대표를 해제하고
지정한 사진만 대표로 둔다(대표는 최대 1장). Where 지정자가 주인이 아니면 거부한다.

**AC-4** When 주인이 사진을 삭제하면, the system shall 사진을 제거한다. Where 삭제자가
주인이 아니면 거부한다. 대표사진이 삭제되면 대표 지정도 함께 해제한다.

**AC-5(연동)** The 미니홈피 메인은 shall 조회자에게 보이는(공개범위 통과) 사진 수와
대표사진을 노출하되, 대표사진도 공개범위를 따른다(가려지면 노출하지 않는다).

## 검증 매핑

| AC | 테스트 |
| --- | --- |
| AC-1 | `tests/test_photo.py::test_upload_owner_only` |
| AC-2 | `tests/test_photo.py::test_scope_visibility` |
| AC-3 | `tests/test_photo.py::test_cover_single_and_owner_only` |
| AC-4 | `tests/test_photo.py::test_delete_owner_only_and_clears_cover` |
| AC-5 | `tests/test_photo.py::test_minihome_photo_summary` |
| 회귀 | `tests/test_regression.py` (visibility scope 계약) |
