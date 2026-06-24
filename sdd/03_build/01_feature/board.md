# 빌드 요약: 게시판 (현재 상태)

> 03_build: 현재 구현된 범위·모듈·동작만 사실 기준으로 기록.

## 구현 범위

| 도메인 | 코드 | 모듈 |
| --- | --- | --- |
| 게시판 | BOARD-F001/F002/F003 | `server/contexts/board/board.py` |
| 연동 | — | `server/contexts/minihome/minihome.py` (board 주입) |
| 런타임 | BOARD-F004 | `serve.py` (인터랙티브 웹 서버) |

## 현재 동작 (user-visible)

- **작성**: 누구나 글 작성(제목·내용). 주인에게 차단된 사용자는 거부.
- **목록**: 최신 글 우선 정렬(`list_for`).
- **삭제**: 작성자 또는 홈피 주인만(그 외 거부).
- **미니홈피 연동**: 메인 페이로드에 `board_count` 포함.
- **인터랙티브 서버**: `serve.py`가 7개 도메인 서비스를 메모리 상태로 구동하는
  **통합 미니홈피 앱**. 클래식 레이아웃 셸 + 우측 8개 탭(`/?tab=...`) 라우팅.
  - 각 탭이 해당 기능 화면을 렌더하고, 폼 POST(작성/삭제/충전/일촌)는 303 redirect로
    즉시 반영. stdlib `http.server`만 사용(의존성 0), UTF-8 폼 처리.
  - 게시판은 그 중 board 탭(`/board/write`·`/board/delete`).
  - 전체 화면 검증: `sdd/04_verify/02_screen/minihome_app.md`.

## 아키텍처 준수

- bounded context `server/contexts/board/` 추가. 차단 blocks만 공유, 외부 도메인 직접 의존 없음.
- MinihomeService 생성자에 `board=None` optional 주입 → 기존 호출부 비파괴.
- `serve.py`는 런타임 진입점으로 도메인 로직을 그대로 재사용(렌더만 담당).

## 알려진 제약

- 서버 상태는 인메모리(프로세스 재시작 시 시드로 초기화).
- 웹 삭제는 데모 단순화를 위해 주인 권한으로 처리(도메인은 작성자/주인 권한을 모두 지원).
