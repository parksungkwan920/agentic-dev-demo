# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 이 프로젝트는 무엇인가

명세(spec)가 "정답"을 정의함을 보여주는 SDD 교육 데모다. 같은 OTP 기능을 두 번 채점한다:
명세 없이(vibe) 짜면 보통 **1/4**, `spec.md`(AC-1~4)대로 짜면 **4/4**. 채점 기준은 양쪽이 같다.

`init/`(시작점) · `learning/`(힌트 포함 연습) · `complete/`(정답) 세 변형이 같은 인프라를 공유하며 `MyOtp.java`만 다르다.

## 핵심 명령

- `./gradlew grade` — **커스텀 채점 태스크.** `src/main/java/dev/agentic/demo/MyOtp.java`를 AC-1~4로 채점한다. 파일이 없으면 참고 구현(`Impls.SddOtp`, 4/4)으로 폴백한다.
- `./gradlew test` — JUnit 증명 게이트(`ContrastTest`).
- `./gradlew build -x test` — 테스트 없이 빌드.

## 빌드 환경 (필수)

- **JDK 17 필요.** `build.gradle`의 toolchain이 17로 고정돼 있다. `gradle.properties`의 `org.gradle.java.home`이 로컬 JDK 17 경로를 가리켜야 `grade`(JavaExec)가 컴파일된 클래스와 같은 JVM에서 돌아 `UnsupportedClassVersionError`가 안 난다. 이 파일은 로컬 절대경로라 gitignore돼 있다 — 다른 환경이면 경로만 본인 JDK 17 위치로 바꾼다.
- **소스는 UTF-8.** `.java`에 한글 주석이 있다. 한국어 Windows의 javac 기본 인코딩(x-windows-949)이면 깨지므로 파일은 반드시 UTF-8(BOM 없이)로 저장한다. `grade` 실행 시 `-Dfile.encoding=UTF-8`를 함께 준다(`.claude/settings.local.json`에 허용 등록됨). 콘솔에 한글이 깨져 보여도 PASS/FAIL·점수는 정상이다.

## Otp 계약과 수용기준

`Otp` 인터페이스: `issue(email, t)` / `verify(email, code, t)` / `signup(email, code, t)` / `created()`.
시간은 시스템 시계가 아니라 정수 `t`(초)로 주입한다 — sleep 없이 만료를 결정적으로 재현하기 위함이다.

- **AC-1** 정상 발급·검증: 유효한 코드로 가입하면 성공.
- **AC-2** 만료 거부: 발급 후 TTL(300초) 초과면 거부.
- **AC-3** 5회 오류 잠금: 5회 연속 오답이면 이후 정답도 거부.
- **AC-4** 재요청 멱등: 같은 사용자가 두 번 가입해도 계정 1개(`created()`는 `Set`이어야 함).

채점 로직은 `Acceptance.java`가 정본이다(기준당 새 인스턴스로 격리, 예외는 FAIL 처리).

## 데모 규칙

- 바이브 라운드를 재현할 때는 `spec.md`를 보지 말고 짧은 설명만으로 `MyOtp`를 짠다. SDD 라운드에서 `spec.md`를 읽고 4/4로 고친다.
- 포맷터/린터는 의도적으로 없다(학습용 최소 구성).
