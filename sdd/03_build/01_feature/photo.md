# 빌드 요약: 사진첩 (현재 상태)

> 03_build: 현재 구현된 범위·모듈·동작만 사실 기준으로 기록.

## 구현 범위

| 도메인 | 코드 | 모듈 |
| --- | --- | --- |
| 사진첩 | PHOTO-F001/F002/F003 | `server/contexts/photo/photo.py` |
| 공통(횡단) | — | `server/shared/visibility.py` (`can_see_scope` 추가) |
| 연동 | — | `server/contexts/minihome/minihome.py` (photo 주입) |

## 현재 동작 (user-visible)

- **업로드**: 홈피 주인만 사진 업로드 가능(타인 거부). 사진은 공개범위(public/ilchon/private)를 가진다.
- **공개범위 조회**: `list_for(owner, viewer)`가 조회자 종류(owner/ilchon/stranger)에 따라
  볼 수 있는 사진만 반환. public=누구나, ilchon=일촌·본인, private=본인.
- **대표사진**: 주인이 cover 지정(최대 1장, 재지정 시 기존 해제). `cover_for`는 조회자
  공개범위를 따라 가려지면 None.
- **삭제**: 주인만 삭제(타인 거부). 대표사진 삭제 시 대표 지정도 함께 해제.
- **미니홈피 연동**: 메인 페이로드에 조회자 기준 `photo_count`·`photo_cover` 포함.

## 아키텍처 준수

- bounded context `server/contexts/photo/` 추가. 의존 방향 단방향(photo → ilchon 조회).
- 공개범위는 `shared/visibility.can_see_scope`로 일원화 — 방명록의 `can_see_section`과
  같은 모듈에서 관리(컨텐츠 공개범위 규칙 집중).
- MinihomeService 생성자에 `photo=None` optional 주입 → 기존 호출부 비파괴.

## 화면

- 데모 렌더러(`render_minihome_demo.py`)가 사진첩 수·대표사진을 좌측 프로필과
  중앙 메뉴(`사진첩 N`)에 실값 바인딩.
