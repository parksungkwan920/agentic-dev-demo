# 검증 요약: BGM + 미니룸 아이템샵 (retained)

> 04_verify · BGM/SHOP. 둘 다 도토리(acorn) 소비처. 회귀 4분면 기준.

## 게이트

- `python proof/run_proof.py` → exit 0, **62/62 PASS** (기존 53 + BGM 5 + 샵 4).

## EARS AC ↔ 테스트

| AC | 테스트 | 결과 |
| --- | --- | --- |
| BGM AC-1 구매·차감·보유 | `test_bgm.py::test_buy_deducts_and_grants` | PASS |
| BGM AC-2 잔액부족 거부 | `test_bgm.py::test_insufficient_rejected` | PASS |
| BGM AC-3 중복 거부 | `test_bgm.py::test_already_owned_rejected` | PASS |
| BGM AC-4 보유곡만 설정 | `test_bgm.py::test_set_current_owned_only` | PASS |
| BGM AC-5 원장 불변식 | `test_bgm.py::test_balance_equals_ledger` | PASS |
| SHOP AC-1~4 | `test_shop.py::*` (구매/부족/중복/불변식) | PASS |

## 회귀 4분면

| 분면 | 표면 | 결과 |
| --- | --- | --- |
| direct | BgmService/ShopService 구매·보유 | PASS (단위 9) |
| upstream | acorn 잔액(충전) → 구매 입력 | PASS |
| downstream | BGM 탭(재생/구매)·샵 탭(인벤토리)·미니룸 가구 배치 | PASS (런타임) |
| **shared** | **acorn 원장 `balance == sum(ledger)`** — 두 소비처가 차감 | PASS. proof 전체 green + `test_acorn::test_balance_equals_ledger_sum` 무파괴 |

## 런타임 증거 (HTTP)

- BGM 구매: 도토리 970→820(−150, night), 보유곡 추가, placeholder 제거.
- 아이템 구매: 820→620(−200, sofa), 인벤토리 추가, **미니룸 SVG 방에 가구 이모지(🪴🛋️) 배치**.
- 연속 구매 후 잔액 음수 없음(잔액부족 구매는 거부 → ledger 불변).
- 재생: Web Audio API `AudioContext` + `playBgm()` ▶ 버튼(사용자 제스처). 음원 파일 0.

## entry_id 유일성 (구매 핵심 가드)

- BgmService/ShopService가 `_seq` 증가로 `bgm-<id>-<seq>` / `shop-<id>-<seq>` 유일 entry_id 생성.
- 멱등 replay로 차감 누락되는 일 없음 → 매 구매가 ledger에 정확히 1건.

## 잔여 리스크

- BGM은 합성 멜로디(짧은 음표 루프) — 실제 음원 스트리밍 아님(데모, 의존성 0 의도).
- 아이템 배치는 SVG 기본방에서만. 업로드/고정 이미지 모드는 인벤토리 목록만(AC-5 명시).
- 상태 인메모리(재시작 시 시드 초기화).
