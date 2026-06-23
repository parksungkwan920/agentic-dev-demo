# -*- coding: utf-8 -*-
"""회원가입 OTP: 발급·검증·만료·잠금 (TTL + 시도 제한).

EARS 가드레일 AC-1(발급+TTL)·AC-3(5회 잠금)·AC-4(만료) 대응.
clock·otp_gen 을 주입해 결정적으로 테스트한다(실시간·난수 비의존).
"""
import random
import time
from dataclasses import dataclass


@dataclass
class OTPResult:
    status: str  # verified | rejected
    reason: str = ""


class OTPService:
    def __init__(self, *, ttl_s=300, max_attempts=5, clock=None, otp_gen=None):
        self.ttl_s = ttl_s
        self.max_attempts = max_attempts
        # 주입 없으면 실시계/난수 사용. 테스트는 고정 시계·고정 코드를 주입한다.
        self._clock = clock or time.time
        self._gen = otp_gen or (lambda: f"{random.randint(0, 999999):06d}")
        self._store = {}

    def issue(self, email, purpose="signup"):
        """(email, purpose)에 6자리 OTP를 발급하고 발급 시각을 기록한다 (AC-1)."""
        code = self._gen()
        self._store[(email, purpose)] = {
            "code": code, "issued": self._clock(), "attempts": 0, "locked": False}
        return code

    def verify(self, email, code, purpose="signup"):
        """OTP 검증: 없음·잠금·만료·불일치를 구분해 거부, 일치 시 통과."""
        rec = self._store.get((email, purpose))
        if rec is None:
            return OTPResult("rejected", "no_otp")
        if rec["locked"]:
            return OTPResult("rejected", "locked")
        if self._clock() - rec["issued"] > self.ttl_s:  # AC-4: TTL 초과 만료
            return OTPResult("rejected", "expired")
        if code != rec["code"]:
            rec["attempts"] += 1
            if rec["attempts"] >= self.max_attempts:  # AC-3: 5회 누적 시 잠금
                rec["locked"] = True
            return OTPResult("rejected", "wrong_code")
        return OTPResult("verified", "ok")
