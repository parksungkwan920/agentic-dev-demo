# -*- coding: utf-8 -*-
"""즐겨찾기: 다른 미니홈피 북마크(본인 전용).

추가 순서를 유지하고, 자기참조·중복을 거부한다.
"""
from dataclasses import dataclass


@dataclass
class FavoriteResult:
    status: str  # ok | rejected
    reason: str = ""


class FavoriteService:
    def __init__(self):
        self._favs = {}  # owner_id -> [target_id, ...] (추가 순서)

    # --- 추가 (AC-1·AC-2) ---
    def add(self, owner_id, target_id) -> FavoriteResult:
        if not target_id or target_id == owner_id:
            return FavoriteResult("rejected", "invalid")
        lst = self._favs.setdefault(owner_id, [])
        if target_id in lst:
            return FavoriteResult("rejected", "duplicate")
        lst.append(target_id)
        return FavoriteResult("ok", "ok")

    # --- 삭제 (AC-3) ---
    def remove(self, owner_id, target_id) -> FavoriteResult:
        lst = self._favs.get(owner_id, [])
        if target_id in lst:
            lst.remove(target_id)
            return FavoriteResult("ok", "ok")
        return FavoriteResult("rejected", "not_found")

    # --- 조회 (AC-4) ---
    def list_for(self, owner_id):
        return list(self._favs.get(owner_id, []))

    def is_favorite(self, owner_id, target_id) -> bool:
        return target_id in self._favs.get(owner_id, [])

    def count(self, owner_id) -> int:
        return len(self._favs.get(owner_id, []))
