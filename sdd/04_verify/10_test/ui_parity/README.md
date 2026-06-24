# UI parity 스냅샷

- `minihome_main.html`: 미니홈피 메인 화면의 승인된 HTML 스냅샷.
- `server/contexts/minihome/screens.py`의 `render("minihome_main")` 출력과 정확히 일치해야 한다.
- 검증: `tests/test_screen_parity.py` (Playwright exactness gate 대용 — 브라우저 비가용 환경).
