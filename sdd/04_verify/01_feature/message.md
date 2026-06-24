# 검증 요약: 쪽지함 (retained)

> 04_verify: command-level 증거 기준. 추정 금지.

## 게이트 결과

- 명령: `python proof/run_proof.py` → **exit 0**
- 결과: **41/41 PASS** (기존 36 + 쪽지함 5) — `tmp/proof-results.json`

## EARS AC ↔ 테스트 매핑 (전부 PASS)

| AC | 테스트 |
| --- | --- |
| MSG AC-1 전송→안읽음 | `test_message.py::test_send_creates_unread` |
| MSG AC-2 차단 전송 거부 | `test_message.py::test_blocked_sender_rejected` |
| MSG AC-3 읽음 권한(수신자) | `test_message.py::test_read_recipient_only` |
| MSG AC-4 inbox/unread 집계 | `test_message.py::test_inbox_and_unread_count` |
| MSG AC-5 미니홈피 본인 전용 | `test_message.py::test_minihome_message_owner_only` |

## 회귀 범위 (선정)

- direct: 쪽지함(`test_message.py`).
- shared: blocks(방명록과 공유) — 36→41 전수 통과로 비파괴 확인. 방명록 차단 테스트도 동시 green.

## 잔여 리스크

- 쪽지 답장 스레드·알림은 미구현(단건 송수신만).
- 게시판·갤러리·BGM·미니룸 아이템샵은 여전히 deferred.
- 배포(05_operate)는 범위 밖 — 롤아웃 미수행.
