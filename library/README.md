# library — 레거시 strangler 전환 데모 (init / complete)

13강 "레거시를 한 모듈씩 Spring Boot 로 전환합니다" 실습의 러닝 예제입니다.
도서관(도서·회원·대출) 레거시를 앞단 라우터를 두고 모듈 하나씩 신규로 옮기는
strangler 패턴을 실습합니다. Java 17 · Spring Boot 3.5 · Gradle. 같은 예제를 두 형태로 둡니다.

| 폴더 | 버전 | 무엇인가 |
| --- | --- | --- |
| `init/` | 초기 버전 | 강의 시작 상태. `legacy` 패키지(시작 코드) + 라우터 + 공유 저장소 + 수용기준 테스트 + 게이트만 있고, `springboot` 신규 구현은 비어 있으며 `migration.properties` 는 전부 legacy 입니다. 학습자가 발화로 한 모듈씩 채웁니다. |
| `complete/` | 완성 버전 | 세 모듈을 모두 신규로 전환한 완성본. `springboot` 구현 3개 + `migration.properties` 전부 new. 수용기준(AC-1·AC-2) green · 전환 3/3. 정답·대조용. |

## 실습 방법

1. `cd init` 에서 시작합니다. `init/PROMPTS.md` 의 세 발화(도서 → 회원 → 대출)를
   Claude Code 에 순서대로 말하면 `springboot` 신규 구현이 채워지고 `migration.properties`
   가 모듈별로 new 로 바뀝니다.
2. 막히거나 결과를 대조하려면 `complete/` 를 봅니다.

## 각 버전 검증 (동일 명령)

```bash
python3 sdd/99_toolchain/01_automation/run_strangler_check.py   # 전환 상태 게이트
./gradlew test                                                  # 수용기준(AC-1 한도5 · AC-2 연체거부)
```

- `init/` : 전환 0/3(전부 legacy)인데도 수용기준 green. 레거시가 규칙을 지킵니다.
- `complete/` : 전환 3/3(전부 new)이고 수용기준 green. 같은 규칙을 신규 구현이 지킵니다.

전환 전·중간·후 어느 상태든 수용기준은 항상 green 입니다. 모든 요청이 라우터를 통과하고,
legacy·new 가 공유 저장소를 쓰며, 신규 대출이 `CatalogRouter` 로 활성 도서·회원을 부르기 때문입니다.

## 강의 ↔ 단계

| 강의 | 내용 | 산출물 |
| --- | --- | --- |
| S13 1단계 | 도서 모듈 전환 | `springboot/NewBookService` + `module.books=new` |
| S13 2단계 | 회원 모듈 전환 | `springboot/NewMemberService` + `module.members=new` |
| S13 3단계 | 대출 모듈 전환 | `springboot/NewLoanService`(CatalogRouter 사용) + `module.loans=new` |
