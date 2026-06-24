# -*- coding: utf-8 -*-
"""사진첩: 업로드(주인 한정)·공개범위 필터·대표사진(cover)·삭제.

공개범위(public/ilchon/private)는 shared/visibility의 can_see_scope를 재사용한다.
대표사진은 최대 1장이며, 조회 시에도 공개범위를 따른다.
clock을 주입해 업로드 시각을 결정적으로 테스트한다.
"""
from dataclasses import dataclass

from server.shared.visibility import (
    PUBLIC,
    can_see_scope,
    viewer_kind,
)


@dataclass
class Photo:
    photo_id: int
    owner_id: str
    caption: str
    scope: str  # public | ilchon | private
    created_at: float
    is_cover: bool = False
    image_uri: str = ""  # 실제 이미지(data URI). 없으면 placeholder 렌더


@dataclass
class PhotoResult:
    status: str  # ok | rejected
    reason: str = ""
    photo_id: int | None = None


class PhotoService:
    def __init__(self, ilchon, clock=None):
        self.ilchon = ilchon  # is_ilchon 제공
        self._photos: list[Photo] = []
        self._next_id = 1
        self._clock = clock or (lambda: 0.0)

    def _kind(self, owner_id, viewer_id):
        return viewer_kind(viewer_id, owner_id,
                           self.ilchon.is_ilchon(owner_id, viewer_id))

    # --- 업로드 (AC-1): 주인만 ---
    def upload(self, owner_id, uploader_id, caption, *, scope=PUBLIC,
               image_uri="") -> PhotoResult:
        if uploader_id != owner_id:
            return PhotoResult("rejected", "not_owner")
        photo = Photo(self._next_id, owner_id, caption, scope, self._clock(),
                      image_uri=image_uri)
        self._photos.append(photo)
        self._next_id += 1
        return PhotoResult("ok", "ok", photo_id=photo.photo_id)

    # --- 조회 (AC-2): 공개범위 필터 ---
    def list_for(self, owner_id, viewer_id):
        kind = self._kind(owner_id, viewer_id)
        return [p for p in self._photos
                if p.owner_id == owner_id and can_see_scope(kind, p.scope)]

    def count_visible(self, owner_id, viewer_id) -> int:
        return len(self.list_for(owner_id, viewer_id))

    # --- 대표사진 (AC-3·AC-5): 주인 지정, 최대 1장, 공개범위 준수 ---
    def set_cover(self, owner_id, photo_id, requester_id) -> PhotoResult:
        if requester_id != owner_id:
            return PhotoResult("rejected", "not_owner")
        target = next((p for p in self._photos
                       if p.photo_id == photo_id and p.owner_id == owner_id), None)
        if target is None:
            return PhotoResult("rejected", "not_found")
        for p in self._photos:
            if p.owner_id == owner_id:
                p.is_cover = (p is target)  # 기존 대표 해제, 지정만 대표
        return PhotoResult("ok", "ok", photo_id=photo_id)

    def cover_for(self, owner_id, viewer_id):
        """조회자에게 보이는 대표사진. 공개범위에 가려지면 None."""
        kind = self._kind(owner_id, viewer_id)
        cover = next((p for p in self._photos
                      if p.owner_id == owner_id and p.is_cover), None)
        if cover is None or not can_see_scope(kind, cover.scope):
            return None
        return cover

    # --- 삭제 (AC-4): 주인만, 대표 해제 동반 ---
    def delete(self, owner_id, photo_id, requester_id) -> PhotoResult:
        if requester_id != owner_id:
            return PhotoResult("rejected", "not_owner")
        for i, p in enumerate(self._photos):
            if p.photo_id == photo_id and p.owner_id == owner_id:
                self._photos.pop(i)  # 대표였더라도 제거 → 대표 지정 함께 해제
                return PhotoResult("ok", "ok", photo_id=photo_id)
        return PhotoResult("rejected", "not_found")
