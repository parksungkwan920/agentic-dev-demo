# -*- coding: utf-8 -*-
"""사진첩: 업로드 권한·공개범위·대표사진·삭제·미니홈피 연동 (PHOTO AC-1~AC-5)."""


def _ilchon_pair(ilchon, a, b):
    ilchon.request(a, b, "친구", "친구")
    ilchon.accept(a, b)


def test_upload_owner_only(photo):
    # 주인 업로드 허용
    r = photo.upload("owner", "owner", "제주도 여행", scope="public")
    assert r.status == "ok"
    # 타인 업로드 거부 (AC-1)
    bad = photo.upload("owner", "stranger", "몰래올림")
    assert bad.status == "rejected" and bad.reason == "not_owner"
    assert photo.count_visible("owner", "owner") == 1


def test_scope_visibility(photo, ilchon):
    photo.upload("owner", "owner", "공개", scope="public")
    photo.upload("owner", "owner", "일촌만", scope="ilchon")
    photo.upload("owner", "owner", "나만", scope="private")
    # 주인: 전부
    assert photo.count_visible("owner", "owner") == 3
    # 타인: public만
    assert photo.count_visible("owner", "stranger") == 1
    # 일촌: public + ilchon (AC-2)
    _ilchon_pair(ilchon, "owner", "friend")
    assert photo.count_visible("owner", "friend") == 2


def test_cover_single_and_owner_only(photo):
    p1 = photo.upload("owner", "owner", "사진1").photo_id
    p2 = photo.upload("owner", "owner", "사진2").photo_id
    # 타인 지정 거부
    assert photo.set_cover("owner", p1, "stranger").status == "rejected"
    photo.set_cover("owner", p1, "owner")
    photo.set_cover("owner", p2, "owner")  # 재지정 → 기존 해제
    cover = photo.cover_for("owner", "owner")
    assert cover.photo_id == p2  # 대표는 최대 1장 (AC-3)


def test_delete_owner_only_and_clears_cover(photo):
    p1 = photo.upload("owner", "owner", "사진1").photo_id
    photo.set_cover("owner", p1, "owner")
    # 타인 삭제 거부
    assert photo.delete("owner", p1, "stranger").status == "rejected"
    # 주인 삭제 → 대표도 함께 사라짐 (AC-4)
    assert photo.delete("owner", p1, "owner").status == "ok"
    assert photo.cover_for("owner", "owner") is None
    assert photo.count_visible("owner", "owner") == 0


def test_minihome_photo_summary(minihome, photo, ilchon):
    photo.upload("owner", "owner", "대표사진", scope="public")
    photo.upload("owner", "owner", "일촌사진", scope="ilchon")
    cover_id = photo.list_for("owner", "owner")[0].photo_id
    photo.set_cover("owner", cover_id, "owner")
    # 주인 시점: 사진 2장 + 대표 노출
    p_owner = minihome.main("owner", "owner")
    assert p_owner["photo_count"] == 2 and p_owner["photo_cover"] == "대표사진"
    # 타인 시점: public 1장만, 대표(public)도 노출 (AC-5)
    p_str = minihome.main("owner", "stranger")
    assert p_str["photo_count"] == 1 and p_str["photo_cover"] == "대표사진"
