# -*- coding: utf-8 -*-
"""게시판: 작성·차단·삭제 권한·최신순·미니홈피 연동 (BOARD AC-1~AC-5)."""


def test_write_creates_post(board):
    r = board.write("owner", "철수", "제목1", "내용입니다")
    assert r.status == "ok" and r.post_id == 1
    assert board.count("owner") == 1


def test_blocked_author_rejected(board, blocks):
    blocks["owner"] = {"troll"}
    r = board.write("owner", "troll", "스팸", "광고")
    assert r.status == "rejected" and r.reason == "blocked"  # (AC-2)
    assert board.count("owner") == 0


def test_delete_author_or_owner(board):
    pid = board.write("owner", "철수", "글", "내용").post_id
    # 제3자 거부
    assert board.delete("owner", pid, "영희").status == "rejected"
    # 작성자 허용
    assert board.delete("owner", pid, "철수").status == "ok"
    # 주인도 삭제 가능
    pid2 = board.write("owner", "민호", "글2", "내용").post_id
    assert board.delete("owner", pid2, "owner").status == "ok"
    assert board.count("owner") == 0


def test_list_newest_first(board):
    board.write("owner", "철수", "첫글", "1")
    board.write("owner", "영희", "둘째글", "2")
    board.write("owner", "민호", "셋째글", "3")
    titles = [p.title for p in board.list_for("owner")]
    assert titles == ["셋째글", "둘째글", "첫글"]  # 최신순 (AC-4)


def test_minihome_board_count(minihome, board):
    board.write("owner", "철수", "a", "1")
    board.write("owner", "영희", "b", "2")
    # 미니홈피 메인에 게시판 글 수 노출 (AC-5)
    assert minihome.main("owner", "stranger")["board_count"] == 2
