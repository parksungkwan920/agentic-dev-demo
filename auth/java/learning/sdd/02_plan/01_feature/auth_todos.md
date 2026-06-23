# 회원가입 OTP · todos + 실행 계획

- Owner: auth-team · Status: done
- canonical: `sdd/01_planning/01_feature/auth_feature_spec.md` (AC-1~AC-6)

---

## Scope

이메일 OTP 회원가입 한 기능을 **발급 · 검증 · 만료 · 잠금 · 멱등 + 화면 parity**까지
구현·검증한다. 기존 로그인 흐름은 회귀로 보호한다.

엔드포인트: `POST /auth/otp/issue` · `POST /auth/signup` · `POST /auth/login`(회귀).

---

## Acceptance Criteria → 구현 → 검증

| AC | 조건 (EARS) | 구현 | 검증 |
| --- | --- | --- | --- |
| AC-1 | 가입 요청 시 (email, purpose) 6자리 OTP 발급 + TTL 300초 | `OtpService.issue` | `AuthFlowTest#happyPath…` (발급 2xx·`\d{6}`) |
| AC-2 | 유효 OTP 입력 시 계정 생성(201), 실패 시 거부(422) | `SignupService.signup` | `AuthFlowTest#happyPath…`(created) · `#signup_withWrongOtp…`(422) |
| AC-3 | 5회 연속 오답 시 해당 OTP 잠금 | `OtpService.verify` (locked 전환) | 서비스 구현 ✓ · 전용 테스트 없음 (gap) |
| AC-4 | TTL(300초) 경과 시 만료로 거부 | `OtpService.verify` (expired) | 서비스 구현 ✓ · 전용 테스트 없음 (gap) |
| AC-5 | 동일 사용자 재가입 시 멱등 — 계정 중복 0 | `SignupService` + `IdempotencyStore` | 서비스 구현 ✓ · 전용 테스트 없음 (gap) |
| AC-6 | signup_otp 화면이 승인 스냅샷과 일치 | `sdd/04_verify/10_test/ui_parity/signup_otp.html` | `./gradlew uiParity` (회귀 게이트) |
| 회귀 | 기존 로그인 흐름 무손상 | `LoginService.login` | `AuthFlowTest#happyPath…`(login status=ok) |

---

## Execution Checklist (비중첩)

- [x] **T1** @backend-dev  OTP 발급·검증·만료·잠금 — `src/main/java/com/datasense/auth/service/OtpService.java` (AC-1·3·4)
- [x] **T2** @backend-dev  가입 + 멱등 — `src/main/java/com/datasense/auth/service/SignupService.java`, `service/IdempotencyStore.java` (AC-2·5)
- [x] **T3** @frontend-dev OTP 입력 화면 정합 — `sdd/04_verify/10_test/ui_parity/signup_otp.html` (AC-6)
- [x] **T4** @test-dev     proof 게이트 + UI parity — `src/test/java/com/datasense/auth/AuthFlowTest.java`

---

## Regression Scope

- **direct**: 가입·OTP 흐름 (`OtpService`, `SignupService`, `AuthController`)
- **shared**: 로그인(`src/main/java/com/datasense/auth/service/LoginService.java`), 계정 저장소(`repository/AccountRepository.java`)
- 근거: `sdd/02_plan/10_test/regression_verification.md`
  (회원가입이 계정 저장소를 로그인과 공유하므로 회귀 범위를 로그인까지 넓힘)

---

## Validation

- `./gradlew test` → **AuthFlowTest 2/2 PASS** (`tmp/proof-results.json`)
- `./gradlew uiParity` → **PASS** (JUnit 회귀 게이트 기준)
- 빌드: Spring Boot 3.5 / **Java 17 toolchain** (`JAVA_HOME`을 JDK 17로 지정 필요)

---

## 잔여 / 후속 (test coverage gap)

- AC-3(잠금)·AC-4(만료)·AC-5(멱등)은 서비스에 구현돼 있으나 `AuthFlowTest`에 전용 케이스가 없다.
  완결성을 높이려면 다음 테스트 추가를 권장:
  - 5회 오답 후 정답 입력 → 422(locked)
  - 발급 후 TTL 경과 시계 주입 → 422(expired)
  - 동일 idemKey 재가입 → 계정 수 불변·replay
- AC-6은 본 환경에서 결정적 HTML parity로 대체(실 브라우저 픽셀 비교는 데모 경계 밖).
