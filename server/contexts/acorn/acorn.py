# -*- coding: utf-8 -*-
"""도토리: 가상 화폐. 충전·구매·선물 + 원장(ledger) 기반 잔액.

핵심 불변식: 임의 시점에 `balance(user) == sum(ledger where user)`.
잔액을 별도 필드로 신뢰하지 않고 원장 합으로 계산해 정합성을 보장한다.
멱등: 같은 entry_id 재요청은 중복 반영하지 않는다.
"""
from dataclasses import dataclass


@dataclass
class AcornResult:
    status: str  # ok | rejected
    reason: str = ""
    balance: int = 0
    replay: bool = False


@dataclass
class LedgerEntry:
    entry_id: str
    user_id: str
    amount: int  # +credit / -debit
    kind: str    # charge | purchase | gift_out | gift_in
    ref: str = ""


class AcornService:
    def __init__(self, ilchon=None):
        self._ledger: list[LedgerEntry] = []
        self._seen = set()  # entry_id 멱등
        self.ilchon = ilchon  # 선물 시 일촌 여부 확인용 (is_ilchon 제공)

    # --- 조회 ---
    def balance(self, user_id) -> int:
        return sum(e.amount for e in self._ledger if e.user_id == user_id)

    def ledger(self, user_id):
        return [e for e in self._ledger if e.user_id == user_id]

    # --- 변동 (AC-1·AC-2·AC-3·AC-6) ---
    def charge(self, user_id, amount, *, entry_id) -> AcornResult:
        if entry_id in self._seen:
            return AcornResult("ok", "replay", self.balance(user_id), replay=True)
        if amount <= 0:
            return AcornResult("rejected", "bad_amount", self.balance(user_id))
        self._seen.add(entry_id)
        self._ledger.append(LedgerEntry(entry_id, user_id, amount, "charge"))
        return AcornResult("ok", "ok", self.balance(user_id))

    def purchase(self, user_id, amount, *, entry_id, ref="") -> AcornResult:
        if entry_id in self._seen:
            return AcornResult("ok", "replay", self.balance(user_id), replay=True)
        if amount <= 0:
            return AcornResult("rejected", "bad_amount", self.balance(user_id))
        if self.balance(user_id) < amount:
            # 잔액 부족: 잔액·원장 불변 (AC-3)
            return AcornResult("rejected", "insufficient", self.balance(user_id))
        self._seen.add(entry_id)
        self._ledger.append(LedgerEntry(entry_id, user_id, -amount, "purchase", ref))
        return AcornResult("ok", "ok", self.balance(user_id))

    # --- 선물 (AC-4): 원자적, 일촌 한정 ---
    def gift(self, sender_id, target_id, amount, *, entry_id) -> AcornResult:
        if entry_id in self._seen:
            return AcornResult("ok", "replay", self.balance(sender_id), replay=True)
        if amount <= 0:
            return AcornResult("rejected", "bad_amount", self.balance(sender_id))
        if self.ilchon is None or not self.ilchon.is_ilchon(sender_id, target_id):
            return AcornResult("rejected", "not_ilchon", self.balance(sender_id))
        if self.balance(sender_id) < amount:
            return AcornResult("rejected", "insufficient", self.balance(sender_id))
        # 차감·증가를 한 트랜잭션으로: 둘 다 기록되거나 둘 다 안 됨
        self._seen.add(entry_id)
        self._ledger.append(
            LedgerEntry(entry_id, sender_id, -amount, "gift_out", ref=target_id))
        self._ledger.append(
            LedgerEntry(entry_id, target_id, amount, "gift_in", ref=sender_id))
        return AcornResult("ok", "ok", self.balance(sender_id))
