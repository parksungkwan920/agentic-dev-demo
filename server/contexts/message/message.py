# -*- coding: utf-8 -*-
"""쪽지함: 1:1 송수신·읽음 처리·차단·삭제.

차단은 방명록과 동일한 blocks(owner_id -> 차단한 사용자 집합)를 공유한다.
clock을 주입해 전송 시각을 결정적으로 테스트한다.
"""
from dataclasses import dataclass


@dataclass
class Message:
    msg_id: int
    sender_id: str
    recipient_id: str
    content: str
    read: bool
    created_at: float


@dataclass
class MessageResult:
    status: str  # ok | rejected
    reason: str = ""
    msg_id: int | None = None


class MessageService:
    def __init__(self, blocks=None, clock=None):
        self._messages: list[Message] = []
        self._next_id = 1
        self._blocks = blocks if blocks is not None else {}  # owner -> set(blocked)
        self._clock = clock or (lambda: 0.0)

    # --- 전송 (AC-1·AC-2) ---
    def send(self, sender_id, recipient_id, content) -> MessageResult:
        if sender_id in self._blocks.get(recipient_id, set()):
            return MessageResult("rejected", "blocked")
        msg = Message(self._next_id, sender_id, recipient_id,
                      content, False, self._clock())
        self._messages.append(msg)
        self._next_id += 1
        return MessageResult("ok", "ok", msg_id=msg.msg_id)

    # --- 조회 (AC-4): 수신자 본인 기준 ---
    def inbox(self, user_id):
        return [m for m in self._messages if m.recipient_id == user_id]

    def sent(self, user_id):
        return [m for m in self._messages if m.sender_id == user_id]

    def unread_count(self, user_id) -> int:
        return sum(1 for m in self._messages
                   if m.recipient_id == user_id and not m.read)

    # --- 읽음 (AC-3): 수신자만 ---
    def read(self, msg_id, reader_id) -> MessageResult:
        msg = next((m for m in self._messages if m.msg_id == msg_id), None)
        if msg is None:
            return MessageResult("rejected", "not_found")
        if msg.recipient_id != reader_id:
            return MessageResult("rejected", "not_recipient")
        msg.read = True
        return MessageResult("ok", "ok", msg_id=msg_id)

    # --- 삭제: 수신자 또는 발신자 본인 ---
    def delete(self, msg_id, requester_id) -> MessageResult:
        for i, m in enumerate(self._messages):
            if m.msg_id == msg_id:
                if requester_id not in (m.recipient_id, m.sender_id):
                    return MessageResult("rejected", "forbidden")
                self._messages.pop(i)
                return MessageResult("ok", "ok", msg_id=msg_id)
        return MessageResult("rejected", "not_found")
