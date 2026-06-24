# 빌드 요약: 다이어리 (현재 상태)

> 03_build: 현재 구현된 범위·모듈·동작만 사실 기준으로 기록.

## 구현 범위

| 도메인 | 코드 | 모듈 |
| --- | --- | --- |
| 다이어리 | DIARY-F001/F002/F003 | `server/contexts/diary/diary.py` |
| 연동 | — | `server/contexts/minihome/minihome.py` (diary 주입) |

## 현재 동작 (user-visible)

- **작성**: 홈피 주인만 작성(타인 거부). 글은 title·body·mood(기분)·공개범위(scope)를 가진다.
- **공개범위 조회**: `list_for(owner, viewer)`·`get`이 조회자 종류에 따라 필터.
  public=누구나, ilchon=일촌·본인, private=본인. `shared/visibility.can_see_scope` 재사용.
- **삭제**: 주인만(타인 거부).
- **미니홈피 연동**: 2단 가시성 — 먼저 다이어리 **섹션**이 비공개면 일촌·본인만 접근 가능
  (`can_see_section`), 그 안에서 다시 **글별 scope**로 보이는 글 수를 집계. 섹션이 가려진
  조회자에게는 `diary_count = 0`.

## 아키텍처 준수

- bounded context `server/contexts/diary/` 추가. 의존 방향 단방향(diary → ilchon 조회).
- 공개범위는 사진첩과 동일한 `can_see_scope`로 일원화 — 컨텐츠 scope 규칙 집중.
- MinihomeService 생성자에 `diary=None` optional 주입 → 기존 호출부 비파괴.

## 화면

- 데모 렌더러가 중앙 메뉴 `다이어리 🔒 N`에 조회자 기준 실값 바인딩.
