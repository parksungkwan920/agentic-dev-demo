# 쪽지함 · Acceptance Criteria (EARS)

> 01_planning: 요구사항을 검증 가능한 EARS로 정제. 이 명세가 가드레일.
> 도메인 코드: MSG · 차단은 방명록과 동일한 blocks(owner→차단자 집합)를 공유한다.

**AC-1** When 사용자가 다른 사용자에게 쪽지를 보내면, the system shall (sender, recipient,
content, read=false, 시각) 쪽지를 저장한다.

**AC-2** Where 수신자가 발신자를 차단했으면, the system shall 전송을 거부하고 쪽지를
저장하지 않는다.

**AC-3** When 수신자가 받은 쪽지를 읽으면, the system shall 그 쪽지를 read=true로 전이한다.
Where 읽음 처리자가 수신자가 아니면(발신자·제3자) 거부한다.

**AC-4** The system shall 받은 쪽지함(inbox)과 안읽음 수(unread_count)를 수신자 본인 기준으로만
집계한다.

**AC-5(연동)** The 미니홈피 메인은 shall 홈피 주인 본인에게만 쪽지함 카운트(안읽음/전체)를
노출하고, 타인에게는 노출하지 않는다.

## 검증 매핑

| AC | 테스트 |
| --- | --- |
| AC-1 | `tests/test_message.py::test_send_creates_unread` |
| AC-2 | `tests/test_message.py::test_blocked_sender_rejected` |
| AC-3 | `tests/test_message.py::test_read_recipient_only` |
| AC-4 | `tests/test_message.py::test_inbox_and_unread_count` |
| AC-5 | `tests/test_message.py::test_minihome_message_owner_only` |
| 회귀 | `tests/test_regression.py` |
