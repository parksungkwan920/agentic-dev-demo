# 싸이월드(미니홈피) — SDD 데모

`agentic-dev-demo/auth`의 SDD(Spec-Driven Development) 기법을 참조해 만든 강의 데모.
실 개인정보·결제 없음. 도토리 "충전"은 가상 잔액 조작이다.

## 범위 (핵심 슬라이스)

서로 맞물리는 4개 bounded context를 한 덩어리로 구현했다.

- **미니홈피(minihome)**: 메인 조립 + 투데이 카운터(본인 방문 제외) + 공개범위
- **일촌(ilchon)**: 신청·수락(상호)·해제·파도타기, 멱등 신청
- **도토리(acorn)**: 충전·구매·선물, 원장 기반 잔액(`잔액 = sum(ledger)`)
- **방명록(guestbook)**: 작성·삭제(권한)·비밀글 가시성·차단

deferred(BGM·사진첩·미니룸 아이템샵 등)는 `sdd/01_planning/INDEX.md` 참조.

## 구조

```
server/
  contexts/{minihome,ilchon,acorn,guestbook}/   도메인별 모듈
  shared/{idem,visibility}.py                   횡단 공통(멱등·공개범위)
tests/                                          도메인별 + 회귀 + 화면 parity
proof/run_proof.py                              결정적 게이트
sdd/                                            SDD 산출물(planning→build→verify)
```

## 실행

```bash
pip install -r requirements.txt
python -m pytest -q          # 전체 테스트
python proof/run_proof.py    # proof 게이트 → tmp/proof-results.json

python serve.py              # 통합 인터랙티브 미니홈피 → http://127.0.0.1:8000
```

### 통합 미니홈피 앱 (`serve.py`)

클래식 레이아웃 + 우측 8개 탭(홈·프로필·다이어리·사진첩·게시판·방명록·쪽지함·일촌)을
모두 활성화한 실행 가능한 웹앱. 각 탭에서 폼으로 작성/삭제하면 즉시 반영된다.
의존성 0(stdlib `http.server`). 상태는 인메모리(재시작 시 시드 초기화).

## SDD 추적

- `sdd/00_sources` 요구사항 원문 → `sdd/01_planning` EARS AC(가드레일) →
  `sdd/02_plan` 실행 계획 → `sdd/03_build` 구현 요약 → `sdd/04_verify` 검증 요약.
- 각 EARS AC ↔ 테스트 매핑은 `sdd/01_planning/01_feature/*_feature_spec.md`의 "검증 매핑" 표 참조.
