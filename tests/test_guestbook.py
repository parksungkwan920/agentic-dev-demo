# -*- coding: utf-8 -*-
"""방명록: 작성·비밀글 가시성·삭제 권한·차단 (GUEST AC-1~AC-4)."""


def test_create_entry(guestbook):
    gb, _ = guestbook
    r = gb.post("owner", "guest", "다녀가요~")
    assert r.status == "ok"
    views = gb.list_for("owner", "owner")
    assert len(views) == 1 and views[0].content == "다녀가요~"


def test_secret_visible_to_owner_and_author_only(guestbook):
    gb, _ = guestbook
    gb.post("owner", "author", "비밀 메모", secret=True)
    # 주인·작성자는 내용 보임
    assert gb.list_for("owner", "owner")[0].content == "비밀 메모"
    assert gb.list_for("owner", "author")[0].content == "비밀 메모"
    # 제3자는 잠김
    other = gb.list_for("owner", "stranger")[0]
    assert other.content is None and other.locked is True


def test_delete_permission(guestbook):
    gb, _ = guestbook
    eid = gb.post("owner", "author", "글").entry_id
    # 제3자 삭제 거부
    assert gb.delete(eid, "stranger").status == "rejected"
    # 작성자 삭제 허용
    assert gb.delete(eid, "author").status == "ok"
    assert gb.list_for("owner", "owner") == []


def test_blocked_user_cannot_post(guestbook, blocks):
    gb, _ = guestbook
    blocks["owner"] = {"troll"}
    r = gb.post("owner", "troll", "스팸")
    assert r.status == "rejected" and r.reason == "blocked"
    assert gb.list_for("owner", "owner") == []
