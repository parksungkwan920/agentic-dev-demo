# -*- coding: utf-8 -*-
"""쪽지함: 송수신·차단·읽음 권한·집계·미니홈피 연동 (MSG AC-1~AC-5)."""


def test_send_creates_unread(message):
    r = message.send("철수", "민키", "안녕! 일촌하자")
    assert r.status == "ok"
    assert message.unread_count("민키") == 1  # 받은 직후 안읽음 (AC-1)


def test_blocked_sender_rejected(message, blocks):
    blocks["민키"] = {"스팸"}  # 민키가 스팸을 차단
    r = message.send("스팸", "민키", "광고입니다")
    assert r.status == "rejected" and r.reason == "blocked"  # (AC-2)
    assert message.unread_count("민키") == 0


def test_read_recipient_only(message):
    mid = message.send("철수", "민키", "잘 지내?").msg_id
    # 발신자/제3자 읽음 거부
    assert message.read(mid, "철수").status == "rejected"
    assert message.read(mid, "영희").status == "rejected"
    # 수신자 읽음 처리 (AC-3)
    assert message.read(mid, "민키").status == "ok"
    assert message.unread_count("민키") == 0


def test_inbox_and_unread_count(message):
    message.send("철수", "민키", "1")
    message.send("영희", "민키", "2")
    message.send("민키", "철수", "답장")  # 민키가 보낸 건 inbox 아님
    assert len(message.inbox("민키")) == 2  # 받은 것만 (AC-4)
    assert len(message.sent("민키")) == 1
    assert message.unread_count("민키") == 2


def test_minihome_message_owner_only(minihome, message):
    message.send("철수", "owner", "쪽지1")
    message.send("영희", "owner", "쪽지2")
    message.read(message.inbox("owner")[0].msg_id, "owner")  # 1개 읽음
    # 주인 본인: 안읽음/전체 노출
    p_owner = minihome.main("owner", "owner")
    assert p_owner["message_unread"] == 1 and p_owner["message_total"] == 2
    # 타인: 쪽지함 카운트 미노출 (AC-5)
    p_str = minihome.main("owner", "stranger")
    assert "message_unread" not in p_str and "message_total" not in p_str
