# -*- coding: utf-8 -*-
"""미니홈피: 투데이 카운터·메인 조립·공개범위 (HOME AC-1~AC-5)."""


def test_today_increments_on_visit(minihome):
    minihome.open("owner", "visitor")
    minihome.open("owner", "visitor2")
    p = minihome.main("owner", "owner")
    assert p["today"] == 2 and p["total"] == 2


def test_owner_visit_not_counted(minihome):
    minihome.open("owner", "owner")  # 본인 방문은 카운트 제외 (AC-2)
    p = minihome.main("owner", "owner")
    assert p["today"] == 0 and p["total"] == 0


def test_main_payload_shape(minihome, guestbook):
    gb, _ = guestbook
    gb.post("owner", "guest", "안녕")
    p = minihome.open("owner", "guest")
    assert p["owner_id"] == "owner"
    assert "minimi_id" in p and "ilchon_count" in p
    assert len(p["recent_guestbook"]) == 1


def test_acorn_balance_owner_only(minihome, acorn):
    acorn.charge("owner", 50, entry_id="c1")
    # 본인 조회: 잔액 포함
    assert minihome.main("owner", "owner")["acorn_balance"] == 50
    # 타인 조회: 잔액 미노출 (AC-4)
    assert "acorn_balance" not in minihome.main("owner", "stranger")


def test_private_section_hidden_for_non_ilchon(minihome, ilchon):
    minihome.set_private("owner", {"diary"})
    # 타인: 비공개 섹션 숨김
    assert minihome.main("owner", "stranger")["sections"] == []
    # 일촌: 노출
    ilchon.request("owner", "friend", "친구", "친구")
    ilchon.accept("owner", "friend")
    assert "diary" in minihome.main("owner", "friend")["sections"]
    # 본인: 노출
    assert "diary" in minihome.main("owner", "owner")["sections"]
