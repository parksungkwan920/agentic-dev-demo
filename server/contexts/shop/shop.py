# -*- coding: utf-8 -*-
"""미니룸 아이템샵: 가구 구매(도토리 소비)·보유(인벤토리).

구매는 acorn 원장으로 처리하고, 구매마다 유일한 entry_id를 써서
`잔액 = sum(ledger)` 불변식을 지킨다. 미니룸 배치는 표현 계층(serve) 담당.
"""
from dataclasses import dataclass

# 아이템 카탈로그: id → (이름, 이모지, 가격)
CATALOG = {
    "plant": ("화분", "🪴", 60),
    "clock": ("벽시계", "🕐", 70),
    "lamp": ("스탠드", "💡", 90),
    "tv": ("티비", "📺", 150),
    "sofa": ("소파", "🛋️", 200),
    "cat": ("고양이", "🐱", 110),
}


@dataclass
class ShopResult:
    status: str  # ok | rejected
    reason: str = ""


class ShopService:
    def __init__(self):
        self._owned = []  # 구매 순서 유지
        self._seq = 0

    def catalog(self):
        return CATALOG

    # --- 구매 (AC-1·AC-2·AC-3·AC-4) ---
    def buy(self, acorn, owner_id, item_id) -> ShopResult:
        if item_id not in CATALOG:
            return ShopResult("rejected", "no_item")
        if item_id in self._owned:
            return ShopResult("rejected", "already")
        name, emoji, price = CATALOG[item_id]
        self._seq += 1
        r = acorn.purchase(owner_id, price,
                           entry_id=f"shop-{item_id}-{self._seq}", ref=name)
        if r.status != "ok":
            return ShopResult("rejected", r.reason)
        self._owned.append(item_id)
        return ShopResult("ok", "ok")

    def owns(self, item_id) -> bool:
        return item_id in self._owned

    def owned(self):
        return list(self._owned)
