package com.datasense.tetris;

import java.util.ArrayList;
import java.util.List;

/**
 * 테트리스 보드의 줄 삭제 규칙(AC-3·AC-4)을 담은 핵심 도메인입니다.
 * 보드는 위에서 아래로 쌓인 행 목록이며(index 0 = 맨 위), 각 행은 칸 배열입니다(false=빈칸, true=채움).
 */
public class Board {
    private final int width;
    private final List<boolean[]> rows;

    public Board(int width, List<boolean[]> rows) {
        this.width = width;
        this.rows = new ArrayList<>(rows);
    }

    public List<boolean[]> rows() {
        return rows;
    }

    /**
     * AC-3·AC-4: 가로로 가득 찬 줄을 모두 지우고, 그 위의 줄을 지운 줄 수만큼 아래로 내립니다.
     * @return 지워진 줄 수
     */
    public int clearFullLines() {
        // TODO: 명세(sdd/01_planning/tetris_spec.md)의 AC-3·AC-4 대로 구현하세요.
        throw new UnsupportedOperationException("TODO: clearFullLines 를 구현하세요");
    }

    private boolean isFull(boolean[] row) {
        for (boolean cell : row) {
            if (!cell) {
                return false;
            }
        }
        return true;
    }
}
