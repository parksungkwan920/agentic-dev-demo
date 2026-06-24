# 화면 검증: 미니홈피 메인 (retained)

> HOME AC-6(화면). 싸이월드 클래식 미니홈피 레이아웃 반영.

## 레이아웃 (참조 이미지 기준)

| 영역 | 구성 | 데이터 바인딩 |
| --- | --- | --- |
| 상단바 | TODAY · TOTAL · "사이좋은 사람들" · URL | `today` / `total` (도메인 실값) |
| 좌 프로필 | 미니미 아바타 · EDIT\|HISTORY · 로고 · 이메일 | `minimi_id` |
| 좌 프로필 | 도토리 잔액 · 일촌 수 | `acorn_balance`(본인만) / `ilchon_count` |
| 중앙 | Updated news · 메뉴 카운트(다이어리/쪽지함 + 사진첩·갤러리·게시판 deferred) | `sections`(다이어리 비공개 🔒) |
| 중앙 | Mini Room("와플준비중") + 미니룸 박스 | 구매 아이템 태그("미니룸 벽지") |
| 중앙 | What friends say(방명록) | `recent_guestbook`(비밀글 가시성 반영) |
| 우 세로탭 | 프로필/다이어리/사진첩/갤러리/게시판/방명록/즐겨찾기 | — |

## 검증

- parity 게이트: `tests/test_screen_parity.py` (2) PASS — `screens.render("minihome_main")`
  ↔ `sdd/04_verify/10_test/ui_parity/minihome_main.html` 일치.
- proof 전체: `python proof/run_proof.py` → exit 0, **25/25 PASS** (회귀 green).
- 실데이터 동작 확인: `python sdd/99_toolchain/01_automation/render_minihome_demo.py --open`
  → `tmp/minihome_demo.html` (TODAY 5 · TOTAL 5 · 도토리 1200 · 일촌 3 · 방명록 3건/비밀글 1).

## 범위/잔여 리스크

- 화면 parity는 시맨틱 뼈대 스냅샷(브라우저 비가용) — 실 픽셀 exactness는 미적용.
- 사진첩·갤러리·게시판·쪽지함·BGM은 deferred로 화면에 0/0 placeholder만 표시(미구현 명시).
- 시각 CSS·아바타·미니룸은 데모 렌더러 표현이며 도메인 계약과 분리.
