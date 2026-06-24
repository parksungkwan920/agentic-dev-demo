# -*- coding: utf-8 -*-
"""미니홈피: 메인 조립 + 투데이 카운터.

일촌·도토리·방명록 컨텍스트를 '조회로만' 조립한다(단방향 의존).
본인 방문은 투데이/누적에 카운트하지 않는다.
공개범위는 shared/visibility 규칙을 재사용한다.
"""
from server.shared.visibility import (
    OWNER,
    can_see_section,
    viewer_kind,
)

RECENT_GUESTBOOK_LIMIT = 5


class MinihomeService:
    def __init__(self, ilchon, acorn, guestbook, photo=None, diary=None,
                 message=None, board=None):
        self.ilchon = ilchon
        self.acorn = acorn
        self.guestbook = guestbook
        self.photo = photo  # 선택: 사진첩 연동 (수·대표사진)
        self.diary = diary  # 선택: 다이어리 연동 (보이는 글 수)
        self.message = message  # 선택: 쪽지함 연동 (본인 안읽음/전체)
        self.board = board  # 선택: 게시판 연동 (글 수)
        # user_id -> {"minimi_id", "today", "total", "private": set()}
        self._homes = {}

    def ensure(self, user_id, *, minimi_id=None, private=None):
        home = self._homes.get(user_id)
        if home is None:
            home = {"minimi_id": minimi_id or f"{user_id}-minimi",
                    "today": 0, "total": 0, "private": set(private or set())}
            self._homes[user_id] = home
        return home

    def set_private(self, user_id, sections):
        self.ensure(user_id)["private"] = set(sections)

    # --- 미니홈피 열기 (AC-1·AC-2): 카운트 + 메인 조립 ---
    def open(self, owner_id, viewer_id):
        home = self.ensure(owner_id)
        if viewer_id != owner_id:  # 본인 방문은 카운트 제외 (AC-2)
            home["today"] += 1
            home["total"] += 1
        return self.main(owner_id, viewer_id)

    # --- 메인 페이로드 조립 (AC-3·AC-4·AC-5) ---
    def main(self, owner_id, viewer_id):
        home = self.ensure(owner_id)
        kind = viewer_kind(viewer_id, owner_id,
                           self.ilchon.is_ilchon(owner_id, viewer_id))

        recent = [v for v in self.guestbook.list_for(owner_id, viewer_id)]
        recent = recent[-RECENT_GUESTBOOK_LIMIT:]

        payload = {
            "owner_id": owner_id,
            "minimi_id": home["minimi_id"],
            "today": home["today"],
            "total": home["total"],
            "ilchon_count": self.ilchon.count(owner_id),
            "recent_guestbook": recent,
        }
        # 도토리 잔액은 홈피 주인 본인에게만 (AC-4)
        if kind == OWNER:
            payload["acorn_balance"] = self.acorn.balance(owner_id)
            # 쪽지함 카운트도 주인 본인에게만 (MSG AC-5)
            if self.message is not None:
                payload["message_unread"] = self.message.unread_count(owner_id)
                payload["message_total"] = len(self.message.inbox(owner_id))
        # 비공개 섹션은 일촌/본인에게만 노출 (AC-5)
        diary_section_visible = can_see_section(kind, "diary" in home["private"])
        if diary_section_visible:
            payload["sections"] = ["diary"]
        else:
            payload["sections"] = []
        # 다이어리 연동: 섹션이 보일 때만 글별 scope로 보이는 글 수 (DIARY AC-4)
        if self.diary is not None:
            payload["diary_count"] = (
                self.diary.count_visible(owner_id, viewer_id)
                if diary_section_visible else 0
            )
        # 게시판 연동: 글 수 (BOARD AC-5)
        if self.board is not None:
            payload["board_count"] = self.board.count(owner_id)
        # 사진첩 연동: 조회자에게 보이는 사진 수·대표사진 (PHOTO AC-5)
        if self.photo is not None:
            payload["photo_count"] = self.photo.count_visible(owner_id, viewer_id)
            cover = self.photo.cover_for(owner_id, viewer_id)
            payload["photo_cover"] = cover.caption if cover else None
        return payload
