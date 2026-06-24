# -*- coding: utf-8 -*-
"""방명록: 작성·삭제(권한)·비밀글 가시성·차단.

비밀글은 홈피 주인과 작성자에게만 내용을 노출한다.
clock을 주입해 작성 시각을 결정적으로 테스트한다.
"""
from dataclasses import dataclass


@dataclass
class GuestEntry:
    entry_id: int
    owner_id: str
    author_id: str
    content: str
    secret: bool
    created_at: float


@dataclass
class GuestView:
    entry_id: int
    owner_id: str
    author_id: str
    secret: bool
    created_at: float
    content: str | None  # 잠긴 비밀글이면 None
    locked: bool


@dataclass
class GuestResult:
    status: str  # ok | rejected
    reason: str = ""
    entry_id: int | None = None


class GuestbookService:
    def __init__(self, blocks=None, clock=None):
        self._entries: list[GuestEntry] = []
        self._next_id = 1
        self._blocks = blocks if blocks is not None else {}  # owner -> set(blocked)
        self._clock = clock or (lambda: 0.0)

    # --- 작성 (AC-1·AC-4) ---
    def post(self, owner_id, author_id, content, *, secret=False) -> GuestResult:
        if author_id in self._blocks.get(owner_id, set()):
            return GuestResult("rejected", "blocked")
        entry = GuestEntry(self._next_id, owner_id, author_id,
                           content, bool(secret), self._clock())
        self._entries.append(entry)
        self._next_id += 1
        return GuestResult("ok", "ok", entry_id=entry.entry_id)

    # --- 조회 (AC-2): 비밀글 가시성 ---
    def list_for(self, owner_id, viewer_id):
        views = []
        for e in self._entries:
            if e.owner_id != owner_id:
                continue
            visible = (not e.secret) or viewer_id in (e.owner_id, e.author_id)
            views.append(GuestView(
                entry_id=e.entry_id, owner_id=e.owner_id, author_id=e.author_id,
                secret=e.secret, created_at=e.created_at,
                content=e.content if visible else None,
                locked=not visible,
            ))
        return views

    # --- 삭제 (AC-3): 홈피 주인 또는 작성자만 ---
    def delete(self, entry_id, requester_id) -> GuestResult:
        for i, e in enumerate(self._entries):
            if e.entry_id == entry_id:
                if requester_id not in (e.owner_id, e.author_id):
                    return GuestResult("rejected", "forbidden", entry_id=entry_id)
                self._entries.pop(i)
                return GuestResult("ok", "ok", entry_id=entry_id)
        return GuestResult("rejected", "not_found", entry_id=entry_id)
