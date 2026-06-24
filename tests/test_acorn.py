# -*- coding: utf-8 -*-
"""도토리: 충전·구매·선물·원장 불변식·멱등 (ACORN AC-1~AC-6)."""


def test_charge_increases_balance_and_ledger(acorn):
    r = acorn.charge("a", 100, entry_id="c1")
    assert r.status == "ok" and r.balance == 100
    assert len(acorn.ledger("a")) == 1


def test_purchase_debits_when_sufficient(acorn):
    acorn.charge("a", 100, entry_id="c1")
    r = acorn.purchase("a", 30, entry_id="p1", ref="item")
    assert r.status == "ok" and r.balance == 70


def test_purchase_rejected_when_insufficient(acorn):
    acorn.charge("a", 20, entry_id="c1")
    r = acorn.purchase("a", 50, entry_id="p1")
    assert r.status == "rejected" and r.reason == "insufficient"
    assert acorn.balance("a") == 20  # 잔액 불변 (AC-3)


def test_gift_atomic_and_ilchon_only(acorn, ilchon):
    acorn.charge("a", 100, entry_id="c1")
    # 일촌 아님 → 거부
    r0 = acorn.gift("a", "b", 40, entry_id="g0")
    assert r0.status == "rejected" and r0.reason == "not_ilchon"
    assert acorn.balance("a") == 100 and acorn.balance("b") == 0
    # 일촌 맺고 선물 → 원자적 이전
    ilchon.request("a", "b", "친구", "친구")
    ilchon.accept("a", "b")
    r1 = acorn.gift("a", "b", 40, entry_id="g1")
    assert r1.status == "ok"
    assert acorn.balance("a") == 60 and acorn.balance("b") == 40


def test_balance_equals_ledger_sum(acorn, ilchon):
    ilchon.request("a", "b", "친구", "친구")
    ilchon.accept("a", "b")
    acorn.charge("a", 100, entry_id="c1")
    acorn.purchase("a", 25, entry_id="p1")
    acorn.gift("a", "b", 10, entry_id="g1")
    # 불변식: 잔액 == 원장 합 (AC-5)
    for user in ("a", "b"):
        assert acorn.balance(user) == sum(e.amount for e in acorn.ledger(user))


def test_charge_idempotent(acorn):
    r1 = acorn.charge("a", 100, entry_id="c1")
    r2 = acorn.charge("a", 100, entry_id="c1")  # 같은 entry_id 재요청
    assert r2.replay is True
    assert acorn.balance("a") == 100  # 중복 반영 없음 (AC-6)
