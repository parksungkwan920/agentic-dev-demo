# -*- coding: utf-8 -*-
"""멱등 처리: idempotency_key로 중복 가입을 차단한다 (AC-5)."""
import hashlib
import json


def idempotency_key(payload: dict) -> str:
    """페이로드를 정규화(sort_keys)해 안정적인 멱등 키를 만든다."""
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class IdempotencyStore:
    def __init__(self):
        self._seen = {}

    def issue_once(self, key, fn):
        """같은 키면 최초 결과를 replay로 반환, 아니면 fn()을 1회 실행해 저장한다."""
        if key in self._seen:
            return self._seen[key], True
        result = fn()
        self._seen[key] = result
        return result, False
