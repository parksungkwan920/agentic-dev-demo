# -*- coding: utf-8 -*-
"""BGM: 곡 구매(도토리 소비)·보유·현재곡 설정.

구매는 acorn 원장으로 처리하고, 구매마다 유일한 entry_id를 써서
`잔액 = sum(ledger)` 불변식을 지킨다. 재생(멜로디 합성)은 표현 계층(serve) 담당.
"""
from dataclasses import dataclass

# 곡 카탈로그: id → (제목, 가격)
CATALOG = {
    "spring": ("봄날의 햇살", 100),
    "night": ("별이 빛나는 밤", 150),
    "rain": ("창밖의 빗소리", 120),
}


@dataclass
class BgmResult:
    status: str  # ok | rejected
    reason: str = ""


class BgmService:
    def __init__(self):
        self._owned = set()
        self._current = None
        self._seq = 0  # entry_id 유일성 보장

    def catalog(self):
        return CATALOG

    # --- 구매 (AC-1·AC-2·AC-3·AC-5) ---
    def buy(self, acorn, owner_id, song_id) -> BgmResult:
        if song_id not in CATALOG:
            return BgmResult("rejected", "no_song")
        if song_id in self._owned:
            return BgmResult("rejected", "already")  # 중복 차감 방지
        title, price = CATALOG[song_id]
        self._seq += 1
        r = acorn.purchase(owner_id, price,
                           entry_id=f"bgm-{song_id}-{self._seq}", ref=title)
        if r.status != "ok":  # 잔액 부족 등 → 보유 불변
            return BgmResult("rejected", r.reason)
        self._owned.add(song_id)
        if self._current is None:
            self._current = song_id
        return BgmResult("ok", "ok")

    # --- 현재곡 (AC-4) ---
    def set_current(self, song_id) -> BgmResult:
        if song_id not in self._owned:
            return BgmResult("rejected", "not_owned")
        self._current = song_id
        return BgmResult("ok", "ok")

    def owns(self, song_id) -> bool:
        return song_id in self._owned

    def owned(self):
        return [s for s in CATALOG if s in self._owned]

    def current(self):
        return self._current
