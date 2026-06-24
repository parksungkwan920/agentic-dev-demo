# -*- coding: utf-8 -*-
"""다이어리: 작성 권한·공개범위·삭제·미니홈피 연동 (DIARY AC-1~AC-4)."""


def _ilchon_pair(ilchon, a, b):
    ilchon.request(a, b, "친구", "친구")
    ilchon.accept(a, b)


def test_write_owner_only(diary):
    r = diary.write("owner", "owner", "오늘의 일기", "행복했다", mood="😊", scope="public")
    assert r.status == "ok"
    # 타인 작성 거부 (AC-1)
    bad = diary.write("owner", "stranger", "몰래", "씀")
    assert bad.status == "rejected" and bad.reason == "not_owner"
    assert diary.count_visible("owner", "owner") == 1


def test_scope_visibility(diary, ilchon):
    diary.write("owner", "owner", "공개일기", "...", scope="public")
    diary.write("owner", "owner", "일촌일기", "...", scope="ilchon")
    diary.write("owner", "owner", "비밀일기", "...", scope="private")
    # 주인: 전부 / 타인: public만 / 일촌: public+ilchon (AC-2)
    assert diary.count_visible("owner", "owner") == 3
    assert diary.count_visible("owner", "stranger") == 1
    _ilchon_pair(ilchon, "owner", "friend")
    assert diary.count_visible("owner", "friend") == 2
    # private 글은 일촌도 조회 불가
    pid = [d for d in diary.list_for("owner", "owner") if d.scope == "private"][0].entry_id
    assert diary.get(pid, "owner", "friend") is None
    assert diary.get(pid, "owner", "owner") is not None


def test_delete_owner_only(diary):
    eid = diary.write("owner", "owner", "글", "내용").entry_id
    assert diary.delete("owner", eid, "stranger").status == "rejected"
    assert diary.delete("owner", eid, "owner").status == "ok"
    assert diary.count_visible("owner", "owner") == 0


def test_minihome_diary_count(minihome, diary):
    diary.write("owner", "owner", "공개", "...", scope="public")
    diary.write("owner", "owner", "일촌", "...", scope="ilchon")
    # 다이어리 섹션 비공개 설정
    minihome.set_private("owner", {"diary"})
    # 주인: 섹션 보이고 글 2개
    assert minihome.main("owner", "owner")["diary_count"] == 2
    # 타인: 섹션 자체가 가려져 0 (AC-4)
    assert minihome.main("owner", "stranger")["diary_count"] == 0


def test_minihome_diary_count_public_section(minihome, diary, ilchon):
    diary.write("owner", "owner", "공개", "...", scope="public")
    diary.write("owner", "owner", "일촌", "...", scope="ilchon")
    # 섹션 공개(비공개 설정 안 함) → 타인도 섹션 접근, 단 글별 scope 적용
    assert minihome.main("owner", "stranger")["diary_count"] == 1  # public만
    _ilchon_pair(ilchon, "owner", "friend")
    assert minihome.main("owner", "friend")["diary_count"] == 2  # public+ilchon
