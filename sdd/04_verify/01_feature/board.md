# 검증 요약: 게시판 (retained)

> 04_verify: command-level 증거 기준. 추정 금지.

## 게이트 결과

- 명령: `python proof/run_proof.py` → **exit 0**
- 결과: **46/46 PASS** (기존 41 + 게시판 5) — `tmp/proof-results.json`

## EARS AC ↔ 테스트 매핑 (전부 PASS)

| AC | 테스트 |
| --- | --- |
| BOARD AC-1 작성 | `test_board.py::test_write_creates_post` |
| BOARD AC-2 차단 거부 | `test_board.py::test_blocked_author_rejected` |
| BOARD AC-3 삭제 권한 | `test_board.py::test_delete_author_or_owner` |
| BOARD AC-4 최신순 | `test_board.py::test_list_newest_first` |
| BOARD AC-5 미니홈피 연동 | `test_board.py::test_minihome_board_count` |

## 런타임(이용성) 검증

- `python serve.py` 기동 → `http://127.0.0.1:8000`.
- `POST /board/write`(UTF-8) → HTTP 303 → `GET /`에서 게시글 수 2→3 반영 확인.
- 한글 제목/작성자 정상: UTF-8 폼 전송 시 "한글 제목 테스트 / 클로드" 깨짐 없이 표시.
  - (주의: Git Bash curl은 콘솔 cp949로 한글이 깨질 수 있음 — 클라이언트 인코딩 이슈이며
    브라우저/Python UTF-8 전송은 정상. 서버는 `decode("utf-8")` + `parse_qs`로 올바르게 처리.)

## 회귀 범위 (선정)

- direct: 게시판(`test_board.py`).
- shared: blocks(방명록·쪽지함과 공유) — 41→46 전수 통과로 비파괴 확인.

## 잔여 리스크

- 서버 상태 인메모리(영속성 없음). 동시성/대량 트래픽 미검증.
- 웹 삭제 권한은 주인 단순화(도메인은 작성자 권한도 지원, 테스트로 커버).
- 갤러리·BGM·미니룸 아이템샵은 여전히 deferred.
- 배포(05_operate)는 범위 밖 — 롤아웃 미수행.
