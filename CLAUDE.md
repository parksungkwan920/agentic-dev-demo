# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

싸이월드 미니홈피를 SDD(Spec-Driven Development) 기법으로 만든 강의용 데모다. 의존성은
`pytest` 하나뿐이며, 런타임 웹앱(`serve.py`)도 Python stdlib(`http.server`)만 쓴다.
모든 데이터는 인메모리(데모용 가상, 실 PII·결제 없음)이며 서버 재시작 시 시드로 초기화된다.

## 명령어

```bash
python -m pytest -q                                   # 전체 테스트
python -m pytest tests/test_acorn.py::test_charge_idempotent   # 단일 테스트
python proof/run_proof.py                             # proof 게이트 → exit 0 + tmp/proof-results.json
python serve.py [--port 8000]                         # 통합 인터랙티브 미니홈피 앱
python sdd/99_toolchain/01_automation/render_minihome_demo.py --open   # 정적 화면 스냅샷 데모
```

`proof/run_proof.py`가 완료 판정 게이트다. 작업을 끝내기 전 항상 exit 0 / 전체 PASS를 확인한다.

## SDD 워크플로우 (이 저장소의 핵심 규약)

기능 추가·수정은 항상 `sdd/` 트레일을 따른다. 단계별 디렉토리:

- `sdd/00_sources` 요구사항 원문 → `sdd/01_planning/01_feature/<domain>_feature_spec.md`
  **EARS AC가 가드레일**(각 AC ↔ 테스트 "검증 매핑" 표 포함) → `sdd/02_plan` 실행 계획 →
  `sdd/03_build` 구현 요약 → `sdd/04_verify` 검증 요약(01_feature, 02_screen 등).

**새 도메인 슬라이스를 추가하는 정착된 절차**(9개 도메인이 동일 패턴을 따름):
1. `sdd/01_planning/01_feature/<domain>_feature_spec.md` — EARS AC + 검증 매핑
2. `server/contexts/<domain>/<domain>.py` — 도메인 서비스(dataclass 결과, 인메모리 store, 의존성 주입)
3. `tests/test_<domain>.py` + `conftest.py` 픽스처
4. `serve.py`에 탭 렌더 + POST 라우트 (도메인 **재사용만**, 로직 중복 금지)
5. `python proof/run_proof.py` 통과 확인
6. `sdd/03_build`·`sdd/04_verify`에 구현·검증 요약 기록

**검증 시 회귀 4분면**(SKILL.md 근거): `direct / upstream / downstream / shared`를 고려한다.
`shared` 표면의 대표가 acorn 원장 불변식이며, proof 전체 green이 곧 shared 검증이다.

## 아키텍처

**Bounded context**: 각 도메인은 `server/contexts/<domain>/`에 격리되고, 공통 횡단 관심사는
`server/shared/`에 일원화된다. 도메인은 서로의 내부 store를 직접 건드리지 않고 공개 함수로만 접근한다.

- `server/shared/visibility.py` — 공개범위 판정을 한 곳에 모음. **여러 도메인이 공유**한다:
  - `viewer_kind(viewer, owner, is_ilchon)` → owner/ilchon/stranger
  - `can_see_section(kind, is_private)` — 섹션 통째 비공개(다이어리 섹션)
  - `can_see_scope(kind, scope)` — 컨텐츠 단위 public/ilchon/private (사진첩·갤러리·다이어리)
  - 이 파일을 바꾸면 미니홈피·방명록·사진첩·다이어리 전부 회귀 대상.
- `server/shared/idem.py` — 멱등 키 저장소.

**도토리(acorn) 경제** — `server/contexts/acorn/acorn.py`:
- 잔액을 필드로 신뢰하지 않고 **원장(ledger) 합으로 계산**. 불변식 `balance(user) == sum(ledger)`.
- 충전/구매/선물·BGM·아이템샵 구매가 모두 ledger를 거친다. 구매 시 **entry_id는 반드시 유일**해야
  한다(중복 entry_id는 멱등 replay로 처리돼 차감이 조용히 누락됨). BGM/Shop 서비스는 `_seq`로
  `bgm-<id>-<seq>` 형태 유일 id를 만든다. 잔액 부족·중복 보유는 거부하며 ledger를 건드리지 않는다.

**미니홈피 조립** — `server/contexts/minihome/minihome.py`:
- `main(owner, viewer)`가 ilchon/acorn/guestbook/photo/diary/message/board를 **조회로 조립**한다.
  viewer 시점에 따라 공개범위가 적용되어, 같은 데이터가 주인/일촌/방문자에게 다르게 보인다.
- 본인 방문은 투데이 카운트에서 제외. 도토리·쪽지함은 주인 본인 페이로드에만 포함.

**통합 웹앱** — `serve.py` (런타임 진입점, 도메인 로직 미포함·렌더+라우팅만):
- 클래식 미니홈피 레이아웃 셸 + 우측 세로탭. `_view["who"]`로 시점 전환(주인/일촌/방문자).
- 미니룸은 인라인 SVG 아이소메트릭 방(`render_miniroom`, `_iso`/`_box` 헬퍼). 표시 우선순위는
  **업로드 이미지 > 고정 `static/miniroom.png` > 기본 SVG**. 업로드 이미지는 디코딩해
  `static/miniroom_uploaded.<ext>`로 영속 저장하고 시작 시 복원한다.
- 이미지 업로드는 **서버측 multipart 파싱을 하지 않는다**. 브라우저 JS `FileReader.readAsDataURL`로
  data URI를 만들어 hidden 필드로 일반 POST 전송(인코딩 이슈 회피). `shell()`의 `<script>` 참조.
- BGM 재생은 **Web Audio API 오실레이터 멜로디**(음원 파일 0). 브라우저 자동재생 정책상 반드시
  ▶ 버튼(사용자 제스처)으로만 시작한다.

**테스트**: `conftest.py`의 픽스처는 결정적이다(고정 clock, seed된 rng). `tests/test_regression.py`는
공유 표면(visibility section/scope, idem) 계약 회귀를, `tests/test_screen_parity.py`는
`server/contexts/minihome/screens.py` ↔ `sdd/04_verify/10_test/ui_parity/minihome_main.html`
스냅샷 일치를 검증한다(브라우저 비가용 환경의 UI parity 대용).

## 주의

- 도메인 로직을 `serve.py`에 중복 구현하지 말 것 — 갤러리는 `PhotoService` 두 번째 인스턴스로
  재사용한다(새 도메인 코드 0). 같은 패턴을 유지한다.
- 한글은 UTF-8로 다룬다. Windows Git Bash의 `curl`은 콘솔 cp949로 한글 인자를 깨뜨릴 수 있으니,
  런타임 한글 검증은 Python `urllib`(UTF-8 인코딩)로 한다.
- 새 슬라이스가 acorn을 차감하면 `tests/test_acorn.py::test_balance_equals_ledger_sum` 포함
  proof 전체가 green인지로 원장 불변식(shared 표면)을 확인한다.
