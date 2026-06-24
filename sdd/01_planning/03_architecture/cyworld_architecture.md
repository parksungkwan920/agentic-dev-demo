# 아키텍처 (초안)

> 레퍼런스(`agentic-dev-demo/auth/python`)와 동일하게 **bounded context** 구조를 미러한다.
> 전역 CLAUDE.md는 TS/React를 기본으로 하나, 본 데모는 레퍼런스 일관성을 우선해 **Python** 스택을 따른다.

## 런타임 / 스택

- 언어: Python (레퍼런스 auth 데모와 동일)
- 구조: `server/contexts/<domain>/` 도메인별 모듈 + `server/shared/` 공통
- 저장: 데모용 인메모리 저장소(레퍼런스 패턴) — 운영 시 RDB로 치환 가능하게 repository 경계 유지
- 테스트: `pytest` + UI parity 러너

## Bounded Contexts

```
server/
  contexts/
    minihome/    # 미니홈피 홈, 투데이 카운터, 공개범위 조립
    ilchon/      # 일촌 신청/수락/해제, 파도타기
    acorn/       # 도토리 잔액·원장(ledger)·선물
    guestbook/   # 방명록 작성/삭제/비밀글/차단
  shared/
    idem.py      # 멱등 키 저장소 (도토리 충전·일촌 신청 재사용)
    visibility.py# 공개범위 판정(본인/일촌/타인) 공통 규칙
```

## 컨텍스트 간 의존 (단방향 유지)

- `minihome` → `ilchon`(일촌 수/관계 조회), `acorn`(본인 잔액), `guestbook`(최근 글) **조회만**
- `acorn.gift` → `ilchon`(일촌 여부 확인)
- `guestbook.post` → `ilchon`/차단 목록(작성 권한)
- 도메인은 서로의 내부 저장소를 직접 건드리지 않고 각 context의 공개 함수로만 접근한다.

## 횡단 관심사

- 멱등성: 도토리 충전/선물, 일촌 신청은 `shared/idem.py`를 공유(레퍼런스 `IdempotencyStore` 패턴).
- 공개범위: `shared/visibility.py`에 `viewer ∈ {owner, ilchon, stranger}` 판정 일원화 → 미니홈피·방명록·다이어리가 재사용.
- 정합성: 도토리는 잔액 필드를 신뢰하지 않고 원장 합으로 검증 가능해야 한다(불변식).
