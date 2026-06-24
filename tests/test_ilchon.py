# -*- coding: utf-8 -*-
"""일촌: 신청·수락(상호)·멱등·해제·파도타기 (ILCHON AC-1~AC-6)."""


def test_request_creates_pending(ilchon):
    r = ilchon.request("a", "b", "베프", "베프")
    assert r.status == "pending"
    assert not ilchon.is_ilchon("a", "b")  # 수락 전엔 관계 없음


def test_request_requires_both_nicknames(ilchon):
    r = ilchon.request("a", "b", "베프", "")
    assert r.status == "rejected" and r.reason == "missing_nickname"


def test_accept_creates_mutual(ilchon):
    ilchon.request("a", "b", "베프", "절친")
    r = ilchon.accept("a", "b")
    assert r.status == "accepted"
    assert ilchon.is_ilchon("a", "b") and ilchon.is_ilchon("b", "a")  # 상호


def test_duplicate_request_idempotent(ilchon):
    ilchon.request("a", "b", "베프", "베프")
    ilchon.request("a", "b", "베프", "베프")  # 재신청
    ilchon.accept("a", "b")
    # 이미 일촌인데 재신청 → 중복 관계 없음
    again = ilchon.request("a", "b", "베프", "베프")
    assert again.reason == "already_ilchon"
    assert ilchon.count("a") == 1


def test_break_removes_both_directions(ilchon):
    ilchon.request("a", "b", "베프", "베프")
    ilchon.accept("a", "b")
    ilchon.break_ilchon("a", "b")
    assert not ilchon.is_ilchon("a", "b") and not ilchon.is_ilchon("b", "a")


def test_wave_returns_friend_of_friend(ilchon):
    # a-b, b-c : a의 파도타기 후보는 c (일촌의 일촌, 본인/직접일촌 제외)
    for x, y in [("a", "b"), ("b", "c")]:
        ilchon.request(x, y, "친구", "친구")
        ilchon.accept(x, y)
    assert ilchon.wave("a") == "c"
