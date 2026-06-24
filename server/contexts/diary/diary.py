# -*- coding: utf-8 -*-
"""다이어리: 작성(주인 한정)·공개범위 필터·조회·삭제.

공개범위(public/ilchon/private)는 shared/visibility의 can_see_scope를 재사용한다.
clock을 주입해 작성 시각을 결정적으로 테스트한다.
"""
from dataclasses import dataclass

from server.shared.visibility import (
    PUBLIC,
    can_see_scope,
    viewer_kind,
)


@dataclass
class DiaryEntry:
    entry_id: int
    owner_id: str
    title: str
    body: str
    mood: str       # 기분 (싸이월드 다이어리 감성)
    scope: str      # public | ilchon | private
    created_at: float
    image_uri: str = ""  # 선택 첨부 이미지(data URI)


@dataclass
class DiaryResult:
    status: str  # ok | rejected
    reason: str = ""
    entry_id: int | None = None


class DiaryService:
    def __init__(self, ilchon, clock=None):
        self.ilchon = ilchon  # is_ilchon 제공
        self._entries: list[DiaryEntry] = []
        self._next_id = 1
        self._clock = clock or (lambda: 0.0)

    def _kind(self, owner_id, viewer_id):
        return viewer_kind(viewer_id, owner_id,
                           self.ilchon.is_ilchon(owner_id, viewer_id))

    # --- 작성 (AC-1): 주인만 ---
    def write(self, owner_id, author_id, title, body,
              *, mood="", scope=PUBLIC, image_uri="") -> DiaryResult:
        if author_id != owner_id:
            return DiaryResult("rejected", "not_owner")
        entry = DiaryEntry(self._next_id, owner_id, title, body,
                           mood, scope, self._clock(), image_uri=image_uri)
        self._entries.append(entry)
        self._next_id += 1
        return DiaryResult("ok", "ok", entry_id=entry.entry_id)

    # --- 조회 (AC-2): 공개범위 필터 ---
    def list_for(self, owner_id, viewer_id):
        kind = self._kind(owner_id, viewer_id)
        return [d for d in self._entries
                if d.owner_id == owner_id and can_see_scope(kind, d.scope)]

    def count_visible(self, owner_id, viewer_id) -> int:
        return len(self.list_for(owner_id, viewer_id))

    def get(self, entry_id, owner_id, viewer_id):
        kind = self._kind(owner_id, viewer_id)
        d = next((x for x in self._entries
                  if x.entry_id == entry_id and x.owner_id == owner_id), None)
        if d is None or not can_see_scope(kind, d.scope):
            return None
        return d

    # --- 삭제 (AC-3): 주인만 ---
    def delete(self, owner_id, entry_id, requester_id) -> DiaryResult:
        if requester_id != owner_id:
            return DiaryResult("rejected", "not_owner")
        for i, d in enumerate(self._entries):
            if d.entry_id == entry_id and d.owner_id == owner_id:
                self._entries.pop(i)
                return DiaryResult("ok", "ok", entry_id=entry_id)
        return DiaryResult("rejected", "not_found")
