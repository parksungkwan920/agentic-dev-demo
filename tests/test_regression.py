# -*- coding: utf-8 -*-
"""회귀: 공유 표면(shared/visibility, shared/idem)이 깨지지 않는지 확인.

핵심 슬라이스 추가가 공통 모듈의 계약을 깨지 않음을 보장한다.
"""
from server.shared.idem import IdempotencyStore, idempotency_key
from server.shared.visibility import (
    ILCHON,
    ILCHON_ONLY,
    OWNER,
    PRIVATE,
    PUBLIC,
    STRANGER,
    can_see_scope,
    can_see_section,
    viewer_kind,
)


def test_visibility_contract():
    assert viewer_kind("u", "u", False) == OWNER
    assert viewer_kind("u", "owner", True) == ILCHON
    assert viewer_kind("u", "owner", False) == STRANGER
    # 비공개 섹션: owner/ilchon만 노출, stranger 숨김
    assert can_see_section(OWNER, True) is True
    assert can_see_section(ILCHON, True) is True
    assert can_see_section(STRANGER, True) is False
    assert can_see_section(STRANGER, False) is True


def test_scope_contract():
    # public: 누구나
    assert can_see_scope(STRANGER, PUBLIC) is True
    # ilchon: owner/ilchon만
    assert can_see_scope(ILCHON, ILCHON_ONLY) is True
    assert can_see_scope(STRANGER, ILCHON_ONLY) is False
    # private: owner만
    assert can_see_scope(OWNER, PRIVATE) is True
    assert can_see_scope(ILCHON, PRIVATE) is False


def test_idem_contract():
    store = IdempotencyStore()
    calls = []

    def fn():
        calls.append(1)
        return "v"

    key = idempotency_key({"x": 1})
    r1, replay1 = store.issue_once(key, fn)
    r2, replay2 = store.issue_once(key, fn)
    assert (r1, replay1) == ("v", False)
    assert (r2, replay2) == ("v", True)
    assert len(calls) == 1  # 재요청은 fn 미실행
