"""테트리스 보드의 줄 삭제 규칙(AC-3·AC-4) 핵심 도메인입니다.

보드는 위에서 아래로 쌓인 행 리스트이며(index 0 = 맨 위), 각 행은 칸 튜플입니다(0=빈칸, 1=채움).
"""


def is_full(row):
    """한 줄의 모든 칸이 채워졌는지 판정합니다."""
    return all(cell == 1 for cell in row)


def clear_full_lines(rows, width):
    """AC-3·AC-4: 가득 찬 줄을 모두 지우고, 그 위의 줄을 지운 줄 수만큼 아래로 내립니다.

    (새 보드, 지운 줄 수) 를 돌려줍니다.
    """
    kept = [row for row in rows if not is_full(row)]
    cleared = len(rows) - len(kept)
    empty = tuple(0 for _ in range(width))
    new_rows = [empty] * cleared + kept  # 위에 빈 줄을 보충해 윗줄이 내려온 효과를 만듭니다
    return new_rows, cleared
