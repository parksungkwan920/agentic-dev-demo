---
name: grade
description: MyOtp 구현을 AC-1~4 수용기준으로 채점한다. ./gradlew grade를 JDK 17 + UTF-8로 돌리고 PASS/FAIL과 점수를 해석한다. 사용자가 "채점", "grade", "점수 확인"을 요청하거나 MyOtp 수정 후 결과를 확인할 때 쓴다.
---

# grade — MyOtp 채점

`MyOtp.java`(또는 인자로 받은 클래스)를 `Acceptance`의 AC-1~4 기준으로 채점한다.

## 실행

```bash
./gradlew grade --console=plain --rerun-tasks 2>&1 | grep -aE "PASS|FAIL|[0-9]/[0-9]|BUILD"
```

- `gradle.properties`의 `org.gradle.java.home`이 JDK 17을 가리키므로 별도 `JAVA_HOME` 지정은 불필요하다. 만약 `UnsupportedClassVersionError`가 나면 그 경로가 JDK 17이 아닌 것이니 먼저 확인한다.
- `grep -a`로 거르는 이유: 한글 출력이 콘솔 인코딩 탓에 깨져 binary로 인식될 수 있다. **한글이 깨져 보여도 `PASS`/`FAIL`·점수는 ASCII라 정상이다.**
- 특정 클래스를 채점하려면 인자로 FQCN을 준다(예: `dev.agentic.demo.Impls$SddOtp`는 불가 — `grade`는 무인자 폴백으로 `Impls.SddOtp`를 쓴다). 기본은 `MyOtp`.

## 결과 해석

- **4/4** — AC-1~4 전부 PASS. 명세가 정의한 동작을 모두 만족.
- **1/4** — 보통 AC-1만 PASS(바이브 구현). 빠진 기준을 `spec.md`(`sdd/01_planning/spec.md`)와 대조해 보고한다:
  - AC-2 FAIL → 만료(TTL 300초) 미처리
  - AC-3 FAIL → 5회 오류 잠금 미구현
  - AC-4 FAIL → `created()`가 `List`라 중복 가입 허용(→ `Set`으로)

점수와 빠진 기준을 한국어로 간결히 정리해 사용자에게 전달한다.
