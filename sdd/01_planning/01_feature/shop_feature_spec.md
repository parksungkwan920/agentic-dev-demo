# 미니룸 아이템샵 · Acceptance Criteria (EARS)

> 01_planning: 요구사항을 검증 가능한 EARS로 정제. 이 명세가 가드레일.
> 도메인 코드: SHOP · 도토리(acorn) 소비처. 가구 아이템 구매·보유(인벤토리)·미니룸 배치.

**AC-1** When 주인이 아이템을 구매하고(미보유·잔액 충분) the system shall 도토리를 가격만큼
차감하고 아이템을 보유(인벤토리)에 추가한다.

**AC-2** If 구매 시 잔액이 부족하면, then the system shall 구매를 거부하고 잔액·보유를
변경하지 않는다.

**AC-3** When 이미 보유한 아이템을 재구매하면, the system shall 거부하고 도토리를 중복
차감하지 않는다.

**AC-4** The system shall 모든 구매를 acorn 원장으로 처리해 `잔액 = sum(ledger)` 불변식을
유지한다. 구매마다 유일한 entry_id를 사용한다.

**AC-5(배치)** The 보유 아이템은 shall 미니룸이 기본 SVG 방일 때 방에 추가로 배치되고,
업로드/고정 이미지 모드에서는 인벤토리 목록으로만 표시한다.

## 검증 매핑

| AC | 테스트 |
| --- | --- |
| AC-1 | `tests/test_shop.py::test_buy_deducts_and_grants` |
| AC-2 | `tests/test_shop.py::test_insufficient_rejected` |
| AC-3 | `tests/test_shop.py::test_already_owned_rejected` |
| AC-4 | `tests/test_shop.py::test_balance_equals_ledger` |
| AC-5 | `serve.py` 런타임(SVG 방에 보유 가구 이모지 배치) |
