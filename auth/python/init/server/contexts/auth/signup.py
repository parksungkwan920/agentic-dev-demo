# -*- coding: utf-8 -*-
"""회원가입: OTP 검증 통과 시 계정 생성, 멱등 보장 (AC-2·AC-5)."""
from dataclasses import dataclass, replace

from server.shared.idem import IdempotencyStore, idempotency_key


@dataclass
class SignupResult:
    status: str  # created | rejected
    reason: str = ""
    email: str = ""
    idempotency_key: str = ""
    replay: bool = False


class SignupService:
    def __init__(self, otp, idem=None):
        self.otp = otp
        self.idem = idem or IdempotencyStore()
        self.accounts = {}

    def signup(self, email, code, *, idem_key=None, purpose="signup"):
        # AC-2: OTP 검증 실패면 가입을 거부하고 사유를 그대로 전달한다.
        v = self.otp.verify(email, code, purpose)
        if v.status != "verified":
            return SignupResult("rejected", v.reason, email=email)

        # AC-5: idem_key(미지정 시 email 파생)로 계정 생성을 1회로 보장한다.
        key = idem_key or idempotency_key({"email": email})

        def _create():
            self.accounts[email] = {"email": email}
            return SignupResult("created", "ok", email=email, idempotency_key=key)

        res, replay = self.idem.issue_once(key, _create)
        return replace(res, replay=replay)
