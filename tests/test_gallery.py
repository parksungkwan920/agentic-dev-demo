# -*- coding: utf-8 -*-
"""갤러리: 사진첩 모델(PhotoService) 재사용 + image_uri 보관 (GALLERY AC-1~AC-4).

갤러리는 사진첩과 동일한 공개범위/권한 규칙을 별도 인스턴스로 재사용한다.
"""
from server.contexts.photo.photo import PhotoService


def _ilchon_pair(ilchon, a, b):
    ilchon.request(a, b, "친구", "친구")
    ilchon.accept(a, b)


def test_gallery_reuses_photo_model(ilchon):
    # 사진첩과 별개의 갤러리 인스턴스
    gallery = PhotoService(ilchon=ilchon, clock=lambda: 0.0)
    gallery.upload("owner", "owner", "공개 이미지", scope="public")
    gallery.upload("owner", "owner", "일촌 이미지", scope="ilchon")
    # 업로드 권한·공개범위가 사진첩과 동일하게 적용
    assert gallery.upload("owner", "stranger", "몰래").status == "rejected"
    assert gallery.count_visible("owner", "owner") == 2
    assert gallery.count_visible("owner", "stranger") == 1
    _ilchon_pair(ilchon, "owner", "friend")
    assert gallery.count_visible("owner", "friend") == 2


def test_image_uri_stored(ilchon):
    gallery = PhotoService(ilchon=ilchon, clock=lambda: 0.0)
    uri = "data:image/png;base64,iVBORw0KGgo="
    gallery.upload("owner", "owner", "진짜 사진", scope="public", image_uri=uri)
    item = gallery.list_for("owner", "owner")[0]
    assert item.image_uri == uri  # 실제 이미지 보관 (AC-4)


def test_image_uri_default_empty(ilchon):
    gallery = PhotoService(ilchon=ilchon, clock=lambda: 0.0)
    gallery.upload("owner", "owner", "이미지 없음", scope="public")
    assert gallery.list_for("owner", "owner")[0].image_uri == ""  # 기본 placeholder
