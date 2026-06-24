# 게시판 · Acceptance Criteria (EARS)

> 01_planning: 요구사항을 검증 가능한 EARS로 정제. 이 명세가 가드레일.
> 도메인 코드: BOARD · 차단은 방명록/쪽지함과 동일한 blocks를 공유한다.

**AC-1** When 방문자가 게시판에 글을 작성하면, the system shall (owner, author, title,
content, 시각) 글을 저장한다.

**AC-2** Where 작성자가 홈피 주인에게 차단된 사용자이면, the system shall 작성을 거부한다.

**AC-3** When 작성자 또는 홈피 주인이 글을 삭제하면, the system shall 글을 제거한다.
Where 삭제자가 작성자도 주인도 아니면 거부한다.

**AC-4** The system shall 게시판 목록을 최신 작성 글이 먼저 오도록 정렬해 제공한다.

**AC-5(연동)** The 미니홈피 메인은 shall 게시판 글 수를 노출한다.

## 검증 매핑

| AC | 테스트 |
| --- | --- |
| AC-1 | `tests/test_board.py::test_write_creates_post` |
| AC-2 | `tests/test_board.py::test_blocked_author_rejected` |
| AC-3 | `tests/test_board.py::test_delete_author_or_owner` |
| AC-4 | `tests/test_board.py::test_list_newest_first` |
| AC-5 | `tests/test_board.py::test_minihome_board_count` |
| 회귀 | `tests/test_regression.py` |

> 이용성: 본 도메인은 인터랙티브 웹 서버(`serve.py`)로 실제 글쓰기/목록/삭제가 가능하다.
