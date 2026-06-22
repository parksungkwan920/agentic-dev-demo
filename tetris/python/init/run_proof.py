#!/usr/bin/env python3
"""결정적 proof 게이트(표준 라이브러리만). pytest 없이도 AC-3·AC-4 를 검증합니다.

명세(sdd/01_planning/tetris_spec.md)의 수용기준을 직접 단언으로 확인하고,
통과 수를 출력합니다. contract.json 의 proof 명령이 이 파일을 호출합니다.
"""
from tetris.board import clear_full_lines

CASES = [
    ("AC-3 한 줄 삭제 + 윗줄 하강",
     [(0, 0, 0), (1, 0, 0), (1, 1, 1)], 3,
     lambda rows, n: n == 1 and rows[2] == (1, 0, 0) and rows[0] == (0, 0, 0)),
    ("AC-4 다중 줄 동시 삭제",
     [(1, 0, 1), (1, 1, 1), (1, 1, 1)], 3,
     lambda rows, n: n == 2 and rows[2] == (1, 0, 1)),
    ("가득 찬 줄 없으면 보드 유지",
     [(1, 0, 0), (0, 1, 0)], 3,
     lambda rows, n: n == 0 and len(rows) == 2),
]


def main():
    passed = 0
    for name, rows, width, check in CASES:
        new_rows, cleared = clear_full_lines(rows, width)
        ok = check(new_rows, cleared)
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        passed += 1 if ok else 0
    total = len(CASES)
    print(f"[proof] {'PASS' if passed == total else 'FAIL'} · {passed}/{total} passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
