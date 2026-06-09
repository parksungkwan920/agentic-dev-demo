# 99_toolchain · toolchain 세 갈래

이커머스 데모의 완료 기준은 "사람이 봤다"가 아니라 "게이트가 통과시켰다"입니다.
toolchain 은 세 갈래로 이루어집니다.

## 생성기 (generator) · gen_proof_evidence.py

```
python3 sdd/99_toolchain/01_automation/gen_proof_evidence.py
```

Gradle JUnit XML 결과를 읽어 `sdd/04_verify/10_test/proof_evidence.md` 를 자동
생성합니다. 사람이 테스트 결과를 보고 손으로 증거 문서를 쓰는 대신, 이 스크립트가
'코드가 통과시켰다'는 공식 증거를 만들어냅니다. 먼저 `./gradlew test` 를 실행해
XML 결과를 만들어야 합니다.

## 하네스 (harness) · 두 게이트

### 게이트 1 · 테스트 게이트

```
./gradlew test
```

JUnit 단위 14 + E2E 9 = 23개를 결정적으로 실행합니다. E2E 는 @SpringBootTest +
MockMvc 로 실제 HTTP 라우팅을 통과시킵니다. exit 0 이면 통과입니다.

### 게이트 2 · DDD 경계 게이트

```
python3 sdd/99_toolchain/01_automation/run_arch_check.py
```

두 가지 구조 규칙을 코드로 판정합니다.

- 규칙 1: domain 레이어는 application·infrastructure·web 을 import 하지 않는다. 도메인 순수성을 지킵니다.
- 규칙 2: bounded context 의존 그래프에 순환이 없다. 단방향 의존을 강제합니다.

이 게이트는 모놀리식 안에서 컨텍스트 경계가 무너지는 것을 막습니다. 취소 엔드포인트를
checkout 컨텍스트로 옮긴 이유도 이 게이트가 순환을 잡아냈기 때문입니다.

## 정책 (policy) · 02_policies

`sdd/99_toolchain/02_policies/` 아래에 이 데모가 따르는 규칙을 글로 남깁니다.
DDD 경계 규칙, 테스트 증거 관리 방식 등 팀이 공유해야 할 약속을 적습니다.
