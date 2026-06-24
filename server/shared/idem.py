# -*- coding: utf-8 -*-
"""멱등 처리: 같은 요청 id(entry/payload)로의 중복 반영을 차단한다.

레퍼런스(auth 데모) IdempotencyStore 패턴을 도토리 충전·일촌 신청이 공유한다.
"""
import hashlib
import json


def idempotency_key(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class IdempotencyStore:
    def __init__(self):
        self._seen = {}

    def issue_once(self, key, fn):
        """key가 처음이면 fn()을 실행해 저장, 재요청이면 저장값 + replay=True."""
        if key in self._seen:
            return self._seen[key], True
        result = fn()
        self._seen[key] = result
        return result, False
