# -*- coding: utf-8 -*-
"""공개범위 판정: viewer ∈ {owner, ilchon, stranger} 를 일원화한다.

미니홈피·방명록·다이어리가 동일 규칙을 재사용한다(횡단 관심사).
"""

OWNER = "owner"
ILCHON = "ilchon"
STRANGER = "stranger"

# 컨텐츠 공개범위(scope) — 사진첩 등에서 사용
PUBLIC = "public"
ILCHON_ONLY = "ilchon"
PRIVATE = "private"


def viewer_kind(viewer_id, owner_id, is_ilchon: bool) -> str:
    """조회 주체가 홈피 주인/일촌/타인 중 무엇인지 판정."""
    if viewer_id == owner_id:
        return OWNER
    if is_ilchon:
        return ILCHON
    return STRANGER


def can_see_section(kind: str, is_private: bool) -> bool:
    """비공개 섹션은 owner/ilchon에게만 노출, 타인에게는 숨긴다."""
    if not is_private:
        return True
    return kind in (OWNER, ILCHON)


def can_see_scope(kind: str, scope: str) -> bool:
    """컨텐츠 공개범위(scope) 판정.

    - public: 누구에게나 노출
    - ilchon: owner/ilchon에게만
    - private: owner에게만
    """
    if scope == PUBLIC:
        return True
    if scope == ILCHON_ONLY:
        return kind in (OWNER, ILCHON)
    if scope == PRIVATE:
        return kind == OWNER
    return False
