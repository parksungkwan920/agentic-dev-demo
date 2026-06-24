# 검증 요약: 즐겨찾기 (retained)

> 04_verify · FAV. 회귀 4분면(direct/upstream/downstream/shared) 기준.

## 게이트

- `python proof/run_proof.py` → exit 0, **53/53 PASS** (기존 49 + 즐겨찾기 4).

## EARS AC ↔ 테스트

| AC | 테스트 | 결과 |
| --- | --- | --- |
| FAV AC-1 추가 | `test_favorite.py::test_add` | PASS |
| FAV AC-2 자기/중복 거부 | `test_favorite.py::test_no_self_no_duplicate` | PASS |
| FAV AC-3 삭제 | `test_favorite.py::test_remove` | PASS |
| FAV AC-4 추가 순서 | `test_favorite.py::test_list_order` | PASS |
| FAV AC-5 본인 전용 노출 | 런타임(방문자 비공개) | PASS |

## 회귀 4분면

| 분면 | 표면 | 결과 |
| --- | --- | --- |
| direct | `FavoriteService` 추가/삭제/목록 | PASS (단위 4 + 런타임) |
| upstream | 추가 입력(이름) | PASS |
| downstream | 즐겨찾기 탭 UI(`/fav/add|remove|visit`) | PASS (런타임 HTTP) |
| shared | 없음(독립 도메인, 다른 그래프 미공유) | proof 53/53 비파괴 |

## 런타임 증거 (HTTP)

- 주인 시점: placeholder 제거, 시드 `[병익,효정,수민]`(3), 추가→4, 중복·자기참조 거부(4 유지), 삭제 반영.
- 방문자 시점: "즐겨찾기는 주인만 볼 수 있어요"(AC-5).
- 바로가기: `/fav/visit` → "OO님의 미니홈피로 바로가기!" 안내.

## 잔여 리스크

- 데모는 과니 미니홈피만 존재 → 바로가기는 대상 이름 안내만(실제 이동 없음, 파도타기와 동일 제약).
- 즐겨찾기 대상의 실존 검증 없음(임의 이름 추가 가능) — 데모 단순화.
