# 99_toolchain · toolchain 세 갈래

레거시 strangler 전환 데모의 완료 기준은 "사람이 봤다"가 아니라 "게이트가 통과시켰다"입니다.
toolchain 은 세 갈래(생성기·하네스·정책)로 이루어집니다. 실습은 이 도구들만으로 끝까지 굴러갑니다.

## 생성기 (generator) · 2개

자료를 사람이 손으로 쓰지 않고 코드가 만들어 냅니다.

### gen_strangler_spec.py · 레거시 → SDD 스펙

```
python3 sdd/99_toolchain/01_automation/gen_strangler_spec.py
```

`src/main/java/kr/elice/library/legacy/` 의 레거시 소스와 요구사항 원문을 읽어
`sdd/01_planning/01_feature/{book,member,loan}.md` EARS 스펙을 생성합니다.
서브에이전트는 이 스펙을 보고 `springboot/New*Service` 를 작성합니다.

### gen_proof_evidence.py · 테스트 결과 → 검증 증거

```
./gradlew test    # 먼저 실행해 XML 결과를 만든 뒤
python3 sdd/99_toolchain/01_automation/gen_proof_evidence.py
```

Gradle JUnit XML 을 읽어 `sdd/04_verify/10_test/proof_evidence.md` 를 자동 생성합니다.
'코드가 통과시켰다'는 공식 증거를 사람 대신 만들어 냅니다.

## 하네스 (harness) · 두 게이트

### 게이트 1 · strangler 구조 게이트

```
python3 sdd/99_toolchain/01_automation/run_strangler_check.py
```

`migration.properties` 를 읽어 모듈별 활성 구현(legacy|new)과 전환 진척(0~3/3)을 판정합니다.
new 로 지정한 모듈에 실제 구현이 없으면 FAIL 로 먼저 잡아냅니다.

### 게이트 2 · 수용기준 테스트 게이트

```
./gradlew test
```

`LibraryAcceptanceTest`(전환 전·후 공통 수용기준 3개)와 `AllNewModeTest`(전환 완료 게이트 4개)를
실행합니다. 둘 다 @SpringBootTest + MockMvc 로 실제 HTTP 라우팅을 통과시킵니다. 합계 7개입니다.

## 정책 (policy) · 02_policies

`sdd/99_toolchain/02_policies/strangler-migration-policy.md` 에 전환 규칙을 글로 못 박아 둡니다.
전환 순서(도서→회원→대출), 클래스 이름 규약, 대출의 CatalogRouter 의무 사용, 게이트 통과 순서를
사람이 바뀌어도 같은 방식으로 따르도록 정합니다.

## 실습 하네스 · lab.sh

```
./lab.sh status   # 현재 전환 상태
./lab.sh reset    # 시작 상태로 (springboot·생성 산출물 제거, 전부 legacy)
./lab.sh solve    # ../complete 의 정답 구현 복원 (서브에이전트 폴백)
./lab.sh verify   # 게이트 1 + 게이트 2 실행
```
