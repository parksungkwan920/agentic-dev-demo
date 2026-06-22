"""명세(sdd/01_planning/tetris_spec.md)의 수용기준을 통과하는 pytest 테스트입니다."""
from tetris.board import clear_full_lines


def test_clears_single_full_line():  # AC-3
    rows = [(0, 0, 0), (1, 0, 0), (1, 1, 1)]
    new_rows, cleared = clear_full_lines(rows, 3)
    assert cleared == 1
    assert len(new_rows) == 3
    assert new_rows[2] == (1, 0, 0)  # 위 블록이 한 칸 내려옴
    assert new_rows[0] == (0, 0, 0)  # 맨 위는 빈 줄


def test_clears_multiple_full_lines():  # AC-4
    rows = [(1, 0, 1), (1, 1, 1), (1, 1, 1)]
    new_rows, cleared = clear_full_lines(rows, 3)
    assert cleared == 2
    assert new_rows[2] == (1, 0, 1)


def test_no_full_line_keeps_board():
    rows = [(1, 0, 0), (0, 1, 0)]
    new_rows, cleared = clear_full_lines(rows, 3)
    assert cleared == 0
    assert len(new_rows) == 2
