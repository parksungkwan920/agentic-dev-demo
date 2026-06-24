# 빌드 요약: 싸이월드 핵심 슬라이스 (현재 상태)

> 03_build: 현재 구현된 범위·모듈·동작만 사실 기준으로 기록.

## 구현 범위

| 도메인 | 코드 | 모듈 |
| --- | --- | --- |
| 미니홈피 | HOME-F001/F002 | `server/contexts/minihome/minihome.py`, `screens.py` |
| 일촌 | ILCHON-F001/F002 | `server/contexts/ilchon/ilchon.py` |
| 도토리 | ACORN-F001/F002 | `server/contexts/acorn/acorn.py` |
| 방명록 | GUEST-F001/F002 | `server/contexts/guestbook/guestbook.py` |
| 공통(횡단) | — | `server/shared/idem.py`, `server/shared/visibility.py` |

## 현재 동작 (user-visible)

- **미니홈피**: `open(owner, viewer)`가 투데이/누적 방문수를 갱신(본인 방문 제외)하고,
  미니미/일촌수/최근 방명록을 한 페이로드로 조립. 도토리 잔액은 본인에게만,
  비공개 섹션(diary)은 본인·일촌에게만 노출.
- **일촌**: 호칭쌍이 모두 채워진 신청만 pending 생성 → 수락 시 양방향 관계.
  이미 pending/accepted면 중복 신청 무효(멱등). 해제는 양방향 동시. 파도타기는
  일촌의 일촌 중 무작위(rng 주입으로 결정적).
- **도토리**: 충전/구매/선물 모두 원장(ledger)에 기록되어 `balance = sum(ledger)`.
  잔액 부족 구매는 거부(잔액 불변), 선물은 일촌 한정·원자적, 충전/선물은 entry_id 멱등.
- **방명록**: 작성(차단 사용자 거부), 비밀글은 주인·작성자에게만 내용 노출,
  삭제는 주인·작성자만.

## 아키텍처 준수

- bounded context 구조(`server/contexts/<domain>/`)를 레퍼런스 auth 데모와 동일하게 미러.
- 의존 방향 단방향: minihome → (ilchon·acorn·guestbook) 조회만, acorn.gift → ilchon.
- 멱등·공개범위는 `server/shared/`로 일원화해 도메인 간 재사용.
- 저장은 인메모리(데모). repository 경계를 유지해 RDB 이행 가능.

## 화면

- `screens.render("minihome_main")` → 승인 스냅샷(`sdd/04_verify/10_test/ui_parity/minihome_main.html`)과 일치.
