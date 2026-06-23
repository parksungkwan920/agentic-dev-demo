---
name: lab-verify
description: 이 프로젝트의 3단계 검증 게이트를 순서대로 실행하고 sdd/04_verify에 결과를 기록합니다. arch_check → gradlew test → gen_proof_evidence 순서를 강제합니다.
disable-model-invocation: false
---

이 프로젝트의 검증 게이트를 아래 순서대로 실행하세요. 각 게이트가 실패하면 다음 단계로 넘어가지 않습니다.

## 사전 확인

- 현재 작업 디렉토리가 `ecommerce/java/learning` 인지 확인합니다.
- JAVA_HOME이 JDK 17을 가리키는지 확인합니다.

## 게이트 1 — 구조 게이트

```bash
python sdd/99_toolchain/01_automation/run_arch_check.py
```

- `RESULT: arch PASS` 이면 게이트 2로 진행합니다.
- `FAIL` 이면 즉시 중단하고 위반 내용을 사용자에게 보고합니다.

## 게이트 2 — 행위 게이트

```bash
JAVA_HOME="C:/Program Files/Java/jdk-17" ./gradlew test
```

- `BUILD SUCCESSFUL` 이면 게이트 3으로 진행합니다.
- 실패 시 테스트 출력을 요약해 사용자에게 보고하고 중단합니다.

## 게이트 3 — 증빙 생성

```bash
python sdd/99_toolchain/01_automation/gen_proof_evidence.py
```

- `sdd/04_verify/10_test/proof_evidence.md` 가 생성됩니다.

## 결과 보고

완료 후 사용자에게 아래 형식으로 보고합니다:

```
arch_check:      PASS
gradlew test:    BUILD SUCCESSFUL (N/N)
proof_evidence:  생성 완료 → sdd/04_verify/10_test/proof_evidence.md
```

실패한 게이트가 있으면 해당 항목에 FAIL과 원인을 표시합니다.
