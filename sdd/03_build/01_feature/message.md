# 빌드 요약: 쪽지함 (현재 상태)

> 03_build: 현재 구현된 범위·모듈·동작만 사실 기준으로 기록.

## 구현 범위

| 도메인 | 코드 | 모듈 |
| --- | --- | --- |
| 쪽지함 | MSG-F001/F002/F003 | `server/contexts/message/message.py` |
| 연동 | — | `server/contexts/minihome/minihome.py` (message 주입) |

## 현재 동작 (user-visible)

- **전송**: 1:1 쪽지 송신. 수신자가 발신자를 차단했으면 거부(저장 안 함).
- **차단 공유**: 방명록과 동일한 blocks(owner→차단자 집합) 재사용 — 한 번 차단하면
  방명록·쪽지 모두 막힌다(일관된 차단 정책).
- **읽음**: 받은 쪽지는 수신자만 read 처리(발신자·제3자 거부).
- **집계**: inbox/sent/unread_count는 수신자(본인) 기준.
- **삭제**: 수신자 또는 발신자 본인만.
- **미니홈피 연동**: 홈피 주인 **본인 시점에만** `message_unread`·`message_total` 노출
  (도토리 잔액과 같은 본인 전용 정보군). 타인 시점에는 키 자체가 없음.

## 아키텍처 준수

- bounded context `server/contexts/message/` 추가. 외부 도메인 직접 의존 없음(blocks만 공유 dict).
- MinihomeService 생성자에 `message=None` optional 주입 → 기존 호출부 비파괴.

## 화면

- 데모 렌더러가 중앙 메뉴 `쪽지함 {unread}/{total}`에 본인 기준 실값 바인딩.
