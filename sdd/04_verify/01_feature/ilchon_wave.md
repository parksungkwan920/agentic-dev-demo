# 검증 요약: 일촌 파도타기 (retained)

> 04_verify · ILCHON AC-6(파도타기). **SDD 회귀 4분면(direct/upstream/downstream/shared)** 기준 검증.
> (SKILL.md: "Identify the direct target plus any upstream, downstream, and shared surfaces affected by the change.")

## 변경 요약

- 도메인 `IlchonService.wave()`는 기존 구현. 이번 추가는 **웹앱 파도타기 버튼+결과**(`serve.py`)와
  파도타기가 의미를 갖도록 **일촌의 일촌 시드**(병익↔수민/지호, 효정↔하늘, 계희↔도윤).

## 회귀 4분면

| 분면 | 표면 | 검증 | 결과 |
| --- | --- | --- | --- |
| **direct** | `wave()` — 일촌의 일촌 중 랜덤(본인·직접일촌 제외) | `tests/test_ilchon.py::test_wave_returns_friend_of_friend` + 런타임 20회 분포 | PASS. 결과 `{수민,지호,하늘,도윤}`만, 직접일촌(병익/효정/계희)·본인(과니) 제외 |
| **upstream** | `request`/`accept`가 일촌 그래프를 채움(wave 입력) | `test_ilchon.py::test_request_*`,`test_accept_creates_mutual` | PASS. 시드 friend-of-friend 정상 생성 |
| **downstream** | wave 결과를 소비하는 웹 UI(`/ilchon/wave` → 결과 메시지) | 런타임 HTTP: 버튼·303·결과 렌더·"후보 없음" 안내 | PASS |
| **shared** | 일촌 그래프(`_relations`)를 함께 읽는 표면: `ilchon_count`·`is_ilchon`·`acorn.gift`·photo/diary `can_see_scope` | `python proof/run_proof.py` 전체 | PASS 49/49 (시드 변경이 공유 표면 비파괴) |

## 런타임 증거

- `/?tab=ilchon` 파도타기 버튼 노출, 과니 직접 일촌 수 3 유지(friend-of-friend는 과니 일촌 아님 → `ilchon_count` 불변).
- `POST /ilchon/wave` → 303 → `?tab=ilchon&waved=<대상>` → "🌊 OO님의 미니홈피로 파도타기!" 렌더.
- 후보 없을 때 "파도탈 일촌의 일촌이 없어요" 안내(시드상 항상 후보 존재).

## 잔여 리스크

- 데모는 과니 미니홈피만 존재 → 파도타기는 대상 이름을 안내할 뿐 실제 그 사람 미니홈피로 이동하진 않음.
- 서버 rng는 비결정적(파도타기 무작위성 의도). 단위 테스트는 결정적 rng로 고정.
