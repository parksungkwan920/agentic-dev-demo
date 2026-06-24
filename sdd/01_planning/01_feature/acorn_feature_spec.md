# 도토리 · Acceptance Criteria (EARS)

> 01_planning: 요구사항을 검증 가능한 EARS로 정제. 이 명세가 가드레일.
> 도메인 코드: ACORN · 데모용 가상 화폐(실 결제 아님)

**AC-1** When 사용자가 도토리를 충전하면, the system shall 잔액을 충전량만큼 증가시키고
원장(ledger)에 credit 항목을 기록한다.

**AC-2** When 사용자가 유료 아이템을 구매하고 잔액이 충분하면, the system shall 잔액을
차감하고 원장에 debit 항목을 기록한다.

**AC-3** If 구매 시 잔액이 부족하면, then the system shall 구매를 거부하고 잔액과 원장을
변경하지 않는다.

**AC-4** When 사용자가 일촌에게 도토리를 선물하면, the system shall 보내는 쪽 차감과
받는 쪽 증가를 단일 트랜잭션으로 처리한다(원자성). Where 대상이 일촌이 아니면 선물을 거부한다.

**AC-5** The system shall 모든 도토리 변동을 원장에 남겨 임의 시점에 `잔액 = sum(ledger)`가
성립함을 보장한다.

**AC-6** When 같은 결제/요청 id로 도토리 변동이 재요청되면, the system shall 멱등성을 보장해
변동을 중복 반영하지 않는다.

## 검증 매핑

| AC | 테스트 |
| --- | --- |
| AC-1 | `tests/test_acorn.py::test_charge_increases_balance_and_ledger` |
| AC-2 | `tests/test_acorn.py::test_purchase_debits_when_sufficient` |
| AC-3 | `tests/test_acorn.py::test_purchase_rejected_when_insufficient` |
| AC-4 | `tests/test_acorn.py::test_gift_atomic_and_ilchon_only` |
| AC-5 | `tests/test_acorn.py::test_balance_equals_ledger_sum` |
| AC-6 | `tests/test_acorn.py::test_charge_idempotent` |
| 회귀 | `tests/test_regression.py` |
