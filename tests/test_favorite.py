# -*- coding: utf-8 -*-
"""즐겨찾기: 추가·자기/중복 거부·삭제·순서 (FAV AC-1~AC-4)."""


def test_add(favorite):
    assert favorite.add("과니", "병익").status == "ok"
    assert favorite.is_favorite("과니", "병익")
    assert favorite.count("과니") == 1


def test_no_self_no_duplicate(favorite):
    assert favorite.add("과니", "과니").status == "rejected"  # 자기참조 (AC-2)
    favorite.add("과니", "병익")
    dup = favorite.add("과니", "병익")
    assert dup.status == "rejected" and dup.reason == "duplicate"
    assert favorite.count("과니") == 1


def test_remove(favorite):
    favorite.add("과니", "병익")
    assert favorite.remove("과니", "병익").status == "ok"  # (AC-3)
    assert not favorite.is_favorite("과니", "병익")
    assert favorite.remove("과니", "없는사람").status == "rejected"


def test_list_order(favorite):
    for t in ["병익", "효정", "계희"]:
        favorite.add("과니", t)
    assert favorite.list_for("과니") == ["병익", "효정", "계희"]  # 추가 순서 (AC-4)
