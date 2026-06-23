# 04_verify · strangler 전환 검증

> 세 모듈(도서·회원·대출)을 `springboot` 패키지에 신규 구현하고 전환한 결과입니다.
> `migration.properties` 세 항목이 모두 `new` 로 설정된 상태에서 아래 게이트를 순서대로 통과했습니다.

## 전환 대상

| 모듈 | 클래스 | 빈 이름 | 상태 |
|------|--------|---------|------|
| 도서 | `NewBookService` | `newBookService` | ✅ new |
| 회원 | `NewMemberService` | `newMemberService` | ✅ new |
| 대출 | `NewLoanService` | `newLoanService` | ✅ new |

## 게이트 1 — 구조 게이트

```
$ python sdd/99_toolchain/01_automation/run_strangler_check.py

  - books    → new (springboot/NewBookService: OK)
  - members  → new (springboot/NewMemberService: OK)
  - loans    → new (springboot/NewLoanService: OK)
전환 3/3 전환 완료
RESULT: strangler PASS
```

**판정: PASS**

## 게이트 2 — 행위 게이트

```
$ JAVA_HOME=".../jdk-17" ./gradlew test

BUILD SUCCESSFUL in 3s
4 actionable tasks: 1 from cache, 3 up-to-date
```

**판정: BUILD SUCCESSFUL**

## 게이트 3 — 증빙 생성

```
$ python sdd/99_toolchain/01_automation/gen_proof_evidence.py

[gen_proof_evidence] 7개 테스트 결과 → sdd/04_verify/10_test/proof_evidence.md
  PASS: 통과 7/7
```

자동 생성된 상세 증빙은 [`10_test/proof_evidence.md`](../10_test/proof_evidence.md) 를 참조합니다.

## 핵심 AC 검증 결과

| AC | 설명 | 결과 |
|----|------|------|
| AC-1 | 대출 한도 5권 초과 시 `LOAN_LIMIT_EXCEEDED` | ✅ PASS |
| AC-2 | 연체 중 회원의 신규 대출 `OVERDUE_EXISTS` 거부 | ✅ PASS |
| all-new | `NewLoanService` → `CatalogRouter` → `NewBook/MemberService` 협력 | ✅ PASS |

## 완료 판정

- 구조 게이트: **PASS**
- 행위 게이트: **BUILD SUCCESSFUL** (7/7)
- 증빙 게이트: **PASS**

> 세 게이트 모두 통과. strangler 전환 완료.
