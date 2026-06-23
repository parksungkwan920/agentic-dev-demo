# 회원가입 OTP · todos + 실행 계획

- Owner: auth-team · Status: done
- canonical: sdd/01_planning/01_feature/auth_feature_spec.md

---

## Scope

이메일 OTP 회원가입 기능 (발급·검증·만료·잠금·멱등·화면 parity)

---

## Acceptance Criteria

| Code  | 조건 (EARS) | 테스트 |
| ----- | ----------- | ------ |
| AC-1  | 회원가입 요청 시 (email, purpose) 묶인 6자리 OTP 발급 + TTL 300초 설정 | `test_otp.py` |
| AC-2  | 유효한 OTP 입력 시 계정 생성 완료 | `test_signup.py` |
| AC-3  | 5회 연속 오답 시 해당 OTP 잠금 | `test_otp.py::test_otp_wrong_then_lock` |
| AC-4  | TTL(300초) 경과 시 만료로 거부 | `test_otp.py::test_otp_expiry` |
| AC-5  | 동일 사용자 재가입 요청 시 멱등성 보장 — 계정 중복 생성 없음 | `test_signup.py::test_signup_idempotent` |
| AC-6  | signup_otp 화면이 승인된 디자인 스냅샷과 일치 | `test_screen_parity.py` |
| AC-R  | 기존 로그인 흐름 회귀 없음 | `test_regression.py` |

---

## Execution Checklist

### 1. OTP 발급·검증 (`server/contexts/auth/otp.py`)
- [x] `OTPService.issue(email, purpose)` — 6자리 OTP 생성, 발급 시각 기록(TTL 300초)
- [x] `OTPService.verify(email, code, purpose)` — no_otp·locked·expired·wrong_code 구분
- [x] 오답 누적 5회 도달 시 `locked` 전환 (AC-3)
- [x] 발급 후 TTL 초과 시 `expired` 거부 (AC-4)
- [x] clock·otp_gen 주입으로 결정적 테스트 지원

### 2. 회원가입 플로우 (`server/contexts/auth/signup.py`)
- [x] `SignupService.signup(email, code, idem_key=None, purpose)` — OTP 검증 후 계정 생성
- [x] 검증 실패 시 사유(reason) 그대로 전달하며 거부 (AC-2)
- [x] 멱등성: 동일 idem_key 재요청은 replay로 처리, 계정 중복 생성 0 (AC-5)

### 3. 멱등 처리 (`server/shared/idem.py`)
- [x] `idempotency_key(payload)` — sort_keys 정규화 후 SHA-256
- [x] `IdempotencyStore.issue_once(key, fn)` — 최초 1회 실행, 재호출 시 replay 반환

### 4. 화면 parity (`server/contexts/auth/screens.py`)
- [x] `screens.render("signup_otp")` — 디자인 스냅샷과 일치하는 HTML 렌더 (AC-6)
- [x] `run_ui_parity.py` 실행 — ui_parity 1/1 PASS

### 5. 테스트 (`tests/`) + 픽스처 (`conftest.py`)
- [x] `test_otp.py` — 발급·검증·만료·잠금 케이스
- [x] `test_signup.py` — 정상 가입·오답 거부·멱등 케이스
- [x] `test_screen_parity.py` — UI parity + 필수 요소
- [x] `test_regression.py` — 기존 로그인 흐름 회귀 없음
- [x] `conftest.py` — 고정 시계 + 고정 OTP(`123456`) 픽스처

### 6. DEV 게이트
- [x] 전체 테스트 스위트 green (proof 10/10)
- [x] UI parity diff 0 (1/1)
- [x] 롤백 조건 정의 (`sdd/05_operate/01_runbooks/auth-service.md`)

---

## Regression Scope
- direct: 가입·OTP 흐름 (`test_otp.py`, `test_signup.py`, `test_screen_parity.py`)
- shared: 로그인(`server/contexts/auth/login.py`), 계정 저장소(`SignupService.accounts`)
- 근거: `sdd/02_plan/10_test/regression_verification.md`

---

## Latest Verification

- proof: PASS · 10/10 (`python3 proof/run_proof.py` → exit 0)
- UI parity: PASS · 1/1 (`python3 sdd/99_toolchain/01_automation/run_ui_parity.py`)
