# -*- coding: utf-8 -*-
"""일촌: 신청·수락(상호)·해제·파도타기.

관계는 양방향(상호)으로 표현하고, 신청은 호칭쌍이 모두 채워져야 한다.
이미 pending/accepted인 대상 재신청은 중복 관계를 만들지 않는다(멱등).
rng를 주입해 파도타기를 결정적으로 테스트한다.
"""
import random
from dataclasses import dataclass


@dataclass
class IlchonResult:
    status: str  # pending | accepted | rejected | removed
    reason: str = ""


class IlchonService:
    def __init__(self, rng=None):
        # (requester, target) -> {"nick_req_to_target", "nick_target_to_req"}
        self._pending = {}
        # frozenset({a, b}) 집합: 상호 일촌 관계
        self._relations = set()
        self._rng = rng or random.Random()

    # --- 조회 ---
    @staticmethod
    def _pair(a, b):
        return frozenset({a, b})

    def is_ilchon(self, a, b) -> bool:
        return self._pair(a, b) in self._relations

    def friends(self, user_id):
        out = set()
        for pair in self._relations:
            if user_id in pair:
                out |= {x for x in pair if x != user_id}
        return out

    def count(self, user_id) -> int:
        return len(self.friends(user_id))

    # --- 신청 (AC-1·AC-2·AC-4) ---
    def request(self, requester, target,
                nick_req_to_target, nick_target_to_req) -> IlchonResult:
        if not nick_req_to_target or not nick_target_to_req:
            return IlchonResult("rejected", "missing_nickname")
        if requester == target:
            return IlchonResult("rejected", "self")
        if self.is_ilchon(requester, target):
            return IlchonResult("rejected", "already_ilchon")  # 멱등: 관계 불변
        # 양방향 어느 쪽이든 이미 pending이면 중복 신청을 만들지 않는다
        if (requester, target) in self._pending or (target, requester) in self._pending:
            return IlchonResult("pending", "already_pending")
        self._pending[(requester, target)] = {
            "nick_req_to_target": nick_req_to_target,
            "nick_target_to_req": nick_target_to_req,
        }
        return IlchonResult("pending", "ok")

    # --- 수락 (AC-3) ---
    def accept(self, requester, target) -> IlchonResult:
        if (requester, target) not in self._pending:
            return IlchonResult("rejected", "no_request")
        del self._pending[(requester, target)]
        self._relations.add(self._pair(requester, target))
        return IlchonResult("accepted", "ok")

    # --- 해제 (AC-5) ---
    def break_ilchon(self, a, b) -> IlchonResult:
        pair = self._pair(a, b)
        if pair not in self._relations:
            return IlchonResult("rejected", "not_ilchon")
        self._relations.discard(pair)  # 양방향 동시 해제
        return IlchonResult("removed", "ok")

    # --- 파도타기 (AC-6): 일촌의 일촌 중 무작위 ---
    def wave(self, user_id):
        direct = self.friends(user_id)
        fof = set()
        for f in direct:
            fof |= self.friends(f)
        candidates = sorted(fof - direct - {user_id})
        if not candidates:
            return None
        return self._rng.choice(candidates)
