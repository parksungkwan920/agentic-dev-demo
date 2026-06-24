# -*- coding: utf-8 -*-
"""BGM: 구매(도토리 차감)·잔액부족·중복·현재곡·원장 불변식 (BGM AC-1~AC-5)."""


def _funded(acorn, amount=500):
    acorn.charge("과니", amount, entry_id="seed")
    return acorn


def test_buy_deducts_and_grants(bgm, acorn):
    _funded(acorn)
    r = bgm.buy(acorn, "과니", "spring")  # 100
    assert r.status == "ok" and bgm.owns("spring")
    assert acorn.balance("과니") == 400


def test_insufficient_rejected(bgm, acorn):
    _funded(acorn, 50)
    r = bgm.buy(acorn, "과니", "night")  # 150
    assert r.status == "rejected" and r.reason == "insufficient"
    assert not bgm.owns("night")
    assert acorn.balance("과니") == 50  # 잔액 불변 (AC-2)


def test_already_owned_rejected(bgm, acorn):
    _funded(acorn)
    bgm.buy(acorn, "과니", "spring")
    r = bgm.buy(acorn, "과니", "spring")
    assert r.reason == "already"
    assert acorn.balance("과니") == 400  # 중복 차감 없음 (AC-3)


def test_set_current_owned_only(bgm, acorn):
    _funded(acorn)
    assert bgm.set_current("spring").status == "rejected"  # 미보유
    bgm.buy(acorn, "과니", "spring")
    assert bgm.set_current("spring").status == "ok"
    assert bgm.current() == "spring"


def test_balance_equals_ledger(bgm, acorn):
    _funded(acorn)
    bgm.buy(acorn, "과니", "spring")
    bgm.buy(acorn, "과니", "night")
    # 불변식: 잔액 == 원장 합 (AC-5, 유일 entry_id 검증)
    assert acorn.balance("과니") == sum(e.amount for e in acorn.ledger("과니"))
    assert acorn.balance("과니") == 500 - 100 - 150
