# 기능 명세 (Specification) — 회원가입 (이메일 OTP)

> **단계: Specify (WHAT & WHY)**
> 본 문서는 "무엇을, 왜" 만드는지만 기술한다. 검증 가능한 가드레일(EARS)은
> [`auth_feature_spec.md`](./auth_feature_spec.md), 기술 구현(HOW)은 `02_plan` 이후 단계에서 다룬다.
>
> **SDD 흐름 위치**: `00_sources`(요구사항 원문) → **`01_planning`(본 문서·EARS)** →
> `02_plan`(todos) → `03_build` → `04_verify` → `05_operate`.

## 1. 개요 (Summary)

기존 인증(auth) 기능에 **이메일 OTP 기반 회원가입**을 추가한다. 사용자는 이메일로 발급받은
6자리 일회용 인증번호(OTP)를 검증해야 계정 생성이 완료된다. 무차별 대입·만료·중복 생성을
방어하며, 기존 로그인 흐름은 그대로 유지(무손상)한다.

> 데모용 가상 데이터: 실 개인정보·실명 없음, 이메일은 불투명 예시값(`a@x.com`)만 사용.
> 원문 요구사항: [`../../00_sources/02_requirements/auth-signup.md`](../../00_sources/02_requirements/auth-signup.md)

## 2. 목표 / 비목표 (Goals / Non-Goals)

### 목표
- 이메일 OTP(6자리) 검증을 통과해야만 계정이 생성되는 회원가입 흐름 제공
- 보안 가드레일: OTP 만료(TTL), 오입력 누적 시 잠금, 가입 멱등성 보장
- `signup_otp` 입력 화면이 승인된 디자인 스냅샷과 일치(UI parity)
- 기존 로그인 흐름 회귀 무손상

### 비목표 (현재 범위)
- 실제 메일 발송·실 OTP 채널 (주입형 OTP로 대체, 발급 code를 응답에 노출)
- 비밀번호 기반 가입, 소셜 로그인(OAuth), 휴대폰 SMS 인증
- 실 브라우저(Playwright) 픽셀 비교·컨테이너 부팅 (HTML parity로 대체)

## 3. 사용자 스토리 (User Stories)

| ID | 사용자 스토리 | 우선순위 |
|----|---------------|---------|
| US-1 | 신규 사용자로서, 이메일로 인증번호를 받아 본인 확인 후 가입하고 싶다. | Must |
| US-2 | 신규 사용자로서, 받은 6자리 OTP를 입력해 계정 생성을 완료하고 싶다. | Must |
| US-3 | 사용자로서, 인증번호가 일정 시간이 지나면 만료되어 재발급받고 싶다. | Must |
| US-4 | 운영자로서, 인증번호 무차별 대입을 자동 차단하고 싶다. | Must |
| US-5 | 사용자로서, 가입 요청이 중복 실행돼도 계정이 한 번만 만들어지길 원한다. | Must |
| US-6 | 사용자로서, OTP 입력 화면이 디자인과 동일하게 보이길 원한다. | Should |
| US-7 | 기존 사용자로서, 회원가입 추가 후에도 로그인이 그대로 동작하길 원한다. | Must |

## 4. 기능 요구사항 (Functional Requirements)

### FR-1 OTP 발급
- `POST /auth/otp/issue` — `(email, purpose)` 키에 묶인 6자리 OTP를 발급한다.
- `purpose` 미지정 시 기본값을 사용한다(가입 목적).
- 발급 시 TTL(300초) 타이머를 건다.
- 데모 편의상 발급된 `code`를 응답에 포함한다(실서비스에선 메일 채널로 대체).

### FR-2 OTP 검증 & 가입
- `POST /auth/signup` — `(email, code, purpose, idemKey)`로 OTP를 검증하고 계정을 생성한다.
- 검증 성공 시 계정 생성, 응답 상태 `201 Created` + `status="created"`.
- 검증 실패(불일치·만료·잠금) 시 `422 Unprocessable Entity`.

### FR-3 만료 (TTL)
- 발급 후 300초가 지난 OTP는 만료로 거부한다(검증 실패 처리).

### FR-4 잠금 (Brute-force 방지)
- 동일 OTP에 대해 인증번호를 **5회 연속** 틀리면 해당 OTP를 잠근다.
- 잠금 이후 입력은 정답이어도 거부한다(재발급 필요).

### FR-5 멱등성 (Idempotency)
- 동일 사용자의 가입 요청이 `idemKey`로 재실행돼도 계정을 중복 생성하지 않는다.
- 재요청(replay) 시 최초 결과와 동일한 응답을 반환한다.

### FR-6 화면 정합 (UI Parity)
- `signup_otp` 화면은 승인된 디자인 스냅샷과 일치해야 한다.
- 참조: [`../../04_verify/02_screen/platform/signup.md`](../../04_verify/02_screen/platform/signup.md),
  `../../04_verify/10_test/ui_parity/signup_otp.html`

### FR-7 회귀 (Regression)
- `POST /auth/login` 등 기존 로그인 흐름은 회원가입 추가로 깨지지 않는다.
- 공유 자원: 계정 저장소, 로그인 서비스.

## 5. 비기능 요구사항 (Non-Functional)

- **보안**: OTP는 일회성·시간제한·시도제한. 발급 code 응답 노출은 데모 한정.
- **일관성**: API 응답 형식 일관(성공/실패 모두 `status` 필드 포함).
- **에러 핸들링**: 만료/잠금/불일치를 구분 가능한 결과로 응답(`422`).
- **멱등성**: 동일 `idemKey` 재요청은 부수효과 없이 동일 응답.
- **회귀 안전성**: 공유 자원 변경 시 로그인 회귀 테스트 green 유지.

## 6. 인수 기준 (Acceptance Criteria)

> 정식 가드레일은 EARS 명세([`auth_feature_spec.md`](./auth_feature_spec.md))의 AC-1~AC-6.
> 아래는 본 명세의 사용자 스토리와의 매핑 요약.

| AC (EARS) | 내용 | 관련 FR / US |
|-----------|------|--------------|
| AC-1 | 가입 요청 시 6자리 OTP 발급 + TTL(300s) | FR-1 / US-1 |
| AC-2 | 유효 OTP 입력 시 계정 생성 | FR-2 / US-2 |
| AC-3 | 5회 오입력 시 OTP 잠금 | FR-4 / US-4 |
| AC-4 | TTL(300s) 경과 시 만료 거부 | FR-3 / US-3 |
| AC-5 | 재요청 시 계정 중복 생성 0 (멱등) | FR-5 / US-5 |
| AC-6 | `signup_otp` 화면 스냅샷 일치 | FR-6 / US-6 |
| 회귀 | 기존 로그인 무손상 | FR-7 / US-7 |

## 7. SDD 추적성 (Traceability)

| 단계 | 산출물 |
|------|--------|
| 00_sources | [`auth-signup.md`](../../00_sources/02_requirements/auth-signup.md) — 요구사항 원문 |
| 01_planning | **본 문서** + [`auth_feature_spec.md`](./auth_feature_spec.md)(EARS) |
| 02_plan | [`auth_todos.md`](../../02_plan/01_feature/auth_todos.md) — 실행 체크리스트 |
| 03_build | `../../03_build/01_feature/auth.md` — 구현 노트 |
| 04_verify | `../../04_verify/01_feature/auth.md` — 회귀 4분면 / UI parity |
| 05_operate | `../../05_operate/02_delivery_status/auth_status.md` — 전달 상태 |

## 8. 미해결 질문 (Open Questions)

- OQ-1: OTP 재발급 정책(쿨다운·재발급 횟수 상한)을 어디까지 명세할지.
- OQ-2: 잠금 해제 조건(시간 경과 자동 해제 vs. 재발급만 허용).
- OQ-3: 실 메일 발송 채널 도입 시 `code` 응답 노출 제거 시점.

> 위 항목은 02_plan 단계에서 기본값을 제안하고, 확정은 사용자 결정에 따른다.
