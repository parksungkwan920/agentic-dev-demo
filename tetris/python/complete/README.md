# 테트리스 (파이썬) · 줄 삭제 핸즈온

요구사항 원문(`sdd/00_sources/tetris.md`)을 EARS 명세(`sdd/01_planning/tetris_spec.md`)로,
다시 할 일(`sdd/02_plan/tetris_todos.md`)로 내린 뒤, `tetris/board.py` 의 `clear_full_lines` 를 구현합니다.

```bash
python3 -m compileall -q tetris   # build
python3 run_proof.py              # proof (표준 라이브러리만, AC-3·AC-4)
# 선택: pytest 사용 시
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
python3 -m pytest -q
```

`init/` 에서 시작해 `clear_full_lines` 를 명세대로 채우면 proof 가 통과합니다. `complete/` 는 정답입니다.
