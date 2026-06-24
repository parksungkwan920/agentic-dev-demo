# -*- coding: utf-8 -*-
"""게시판: 글 작성·목록(최신순)·삭제·차단.

차단은 방명록/쪽지함과 동일한 blocks(owner_id -> 차단한 사용자 집합)를 공유한다.
clock을 주입해 작성 시각을 결정적으로 테스트한다.
"""
from dataclasses import dataclass


@dataclass
class BoardPost:
    post_id: int
    owner_id: str
    author_id: str
    title: str
    content: str
    created_at: float


@dataclass
class BoardResult:
    status: str  # ok | rejected
    reason: str = ""
    post_id: int | None = None


class BoardService:
    def __init__(self, blocks=None, clock=None):
        self._posts: list[BoardPost] = []
        self._next_id = 1
        self._blocks = blocks if blocks is not None else {}  # owner -> set(blocked)
        self._clock = clock or (lambda: 0.0)

    # --- 작성 (AC-1·AC-2) ---
    def write(self, owner_id, author_id, title, content) -> BoardResult:
        if author_id in self._blocks.get(owner_id, set()):
            return BoardResult("rejected", "blocked")
        post = BoardPost(self._next_id, owner_id, author_id,
                         title, content, self._clock())
        self._posts.append(post)
        self._next_id += 1
        return BoardResult("ok", "ok", post_id=post.post_id)

    # --- 목록 (AC-4): 최신순 ---
    def list_for(self, owner_id):
        return sorted(
            [p for p in self._posts if p.owner_id == owner_id],
            key=lambda p: p.post_id, reverse=True,
        )

    def count(self, owner_id) -> int:
        return sum(1 for p in self._posts if p.owner_id == owner_id)

    def get(self, owner_id, post_id):
        return next((p for p in self._posts
                     if p.post_id == post_id and p.owner_id == owner_id), None)

    # --- 삭제 (AC-3): 작성자 또는 주인 ---
    def delete(self, owner_id, post_id, requester_id) -> BoardResult:
        for i, p in enumerate(self._posts):
            if p.post_id == post_id and p.owner_id == owner_id:
                if requester_id not in (p.author_id, p.owner_id):
                    return BoardResult("rejected", "forbidden", post_id=post_id)
                self._posts.pop(i)
                return BoardResult("ok", "ok", post_id=post_id)
        return BoardResult("rejected", "not_found", post_id=post_id)
