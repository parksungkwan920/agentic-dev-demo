# -*- coding: utf-8 -*-
"""아이템샵: 구매(도토리 차감)·잔액부족·중복·원장 불변식 (SHOP AC-1~AC-4)."""


def _funded(acorn, amount=500):
    acorn.charge("과니", amount, entry_id="seed")
    return acorn


def test_buy_deducts_and_grants(shop, acorn):
    _funded(acorn)
    r = shop.buy(acorn, "과니", "plant")  # 60
    assert r.status == "ok" and shop.owns("plant")
    assert acorn.balance("과니") == 440


def test_insufficient_rejected(shop, acorn):
    _funded(acorn, 50)
    r = shop.buy(acorn, "과니", "sofa")  # 200
    assert r.status == "rejected" and r.reason == "insufficient"
    assert not shop.owns("sofa")
    assert acorn.balance("과니") == 50


def test_already_owned_rejected(shop, acorn):
    _funded(acorn)
    shop.buy(acorn, "과니", "plant")
    r = shop.buy(acorn, "과니", "plant")
    assert r.reason == "already"
    assert acorn.balance("과니") == 440  # 중복 차감 없음


def test_balance_equals_ledger(shop, acorn):
    _funded(acorn)
    shop.buy(acorn, "과니", "plant")
    shop.buy(acorn, "과니", "lamp")
    assert acorn.balance("과니") == sum(e.amount for e in acorn.ledger("과니"))
    assert shop.owned() == ["plant", "lamp"]  # 구매 순서
