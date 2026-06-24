# 게시판 · todos + 실행 계획

## Scope
미니홈피 게시판 한 도메인을 작성·최신순 목록·삭제·차단 + 미니홈피 연동까지 구현·검증하고,
**실행 가능한 인터랙티브 웹 서버(`serve.py`)로 실제 글쓰기/삭제가 가능**하게 한다.

## Acceptance Criteria
- BOARD AC-1~AC-5 (`sdd/01_planning/01_feature/board_feature_spec.md`) 전부 테스트 통과.
- 차단은 방명록/쪽지함과 동일한 blocks 공유, 회귀 green.
- 브라우저 폼으로 글 작성 시 즉시 목록 반영(런타임 검증).

## Feature Items
| Code       | Use Case                    | Status | Notes |
| ---------- | --------------------------- | ------ | ----- |
| BOARD-F001 | 작성·차단                    | done   | blocks 공유 |
| BOARD-F002 | 최신순 목록·삭제(작성자/주인) | done   |       |
| BOARD-F003 | 미니홈피 연동(글 수)         | done   |       |
| BOARD-F004 | 인터랙티브 웹 서버           | done   | stdlib http.server, 의존성 0 |

## Execution Checklist (비중첩)
- [x] T1 @backend-dev  게시판 도메인 (`server/contexts/board/board.py`)
- [x] T2 @backend-dev  미니홈피 연동 (`server/contexts/minihome/minihome.py`)
- [x] T3 @test-dev     test_board (`tests/test_board.py`)
- [x] T4 @backend-dev  인터랙티브 서버 (`serve.py`) — GET / · POST /board/write · /board/delete
- [x] T5 @test-dev     런타임 검증 (UTF-8 POST → 목록 반영)

## Regression Scope
- direct: 게시판 흐름(`test_board.py`)
- shared: blocks(방명록·쪽지함 공유) → 전수 회귀
- 근거: `sdd/02_plan/10_test/regression_verification.md`

## Validation
- `python proof/run_proof.py` → exit 0, 46/46 PASS.
- 런타임: `python serve.py` 기동 후 POST /board/write → 게시글 수 2→3, 제목/작성자 정상(UTF-8).
