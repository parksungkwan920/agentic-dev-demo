# 발화 대본: Claude Code 로 strangler 전환 실습 (PPT 13강 싱크)

> 아래 세 발화를 Claude Code 에 순서대로 말하면 실습이 끝까지 굴러갑니다. 발화 외에
> 손으로 코드를 짤 필요는 없습니다. 막히면 `./lab.sh solve` 로 완성본을 불러오고,
> 다시 처음부터 하려면 `./lab.sh reset` 으로 시작 상태로 되돌립니다.

## 시작 상태 확인

```bash
./lab.sh status          # 세 모듈 모두 legacy, springboot 0개
./lab.sh verify          # 시작 상태에서도 수용기준 green (레거시가 규칙을 지킴)
```

## 전환 규약 (Claude 가 지켜야 할 약속)

- 신규 구현은 `src/main/java/kr/elice/library/springboot/` 에 둡니다.
- 클래스 이름은 `NewBookService`·`NewMemberService`·`NewLoanService` 로 합니다.
  (스프링 기본 빈 이름이 `newBookService` … 가 되어 라우터가 자동 선택합니다.)
- 각 신규 구현은 `kr.elice.library.api` 의 같은 인터페이스를 구현합니다.
- "라우터를 신규로 보낸다" = `src/main/resources/migration.properties` 의 해당 모듈을 `new` 로 바꿉니다.
- 신규 대출은 도서·회원을 직접 부르지 않고 `platform.CatalogRouter` 로 활성 구현을 받아 호출합니다.

## 1단계 · 도서 모듈 (가장 독립적)

> legacy 패키지의 도서(Book) 모듈을 SDD 스펙으로 정리하고, 그 스펙으로
> springboot 패키지에 NewBookService 를 구현해줘. 그리고 migration.properties
> 에서 module.books 만 new 로 바꿔서 라우터가 도서만 신규로 보내게 해줘.
> 회원과 대출은 legacy 그대로 둬.

확인:
```bash
./lab.sh verify          # 도서=new, 회원·대출=legacy 인데도 수용기준 green
```

## 2단계 · 회원 모듈

> 같은 방식으로 legacy 회원(Member) 모듈을 springboot 의 NewMemberService 로
> 구현하고, migration.properties 의 module.members 를 new 로 바꿔줘.

확인: `./lab.sh verify`

## 3단계 · 대출 모듈 (도서·회원에 의존 → 마지막)

> legacy 대출(Loan) 모듈을 springboot 의 NewLoanService 로 구현해줘. 대출은
> CatalogRouter 로 활성 도서·회원 구현을 받아 호출하고, AC-1 대출 한도 5권과
> AC-2 연체 시 거부를 그대로 지켜줘. migration.properties 의 module.loans 를
> new 로 바꿔서 세 모듈을 모두 신규로 전환해줘.

확인 — 구조 게이트 → 행위 채점기 → **전환 완료 게이트** 순서로 실행합니다:

```bash
# 1. 전환 상태: 세 모듈이 모두 new 인지 확인
python3 sdd/99_toolchain/01_automation/run_strangler_check.py   # 전환 3/3

# 2. 행위 채점기: 전환 전·후 공통 수용기준 (LibraryAcceptanceTest 3개)
./lab.sh verify

# 3. 전환 완료 게이트: 신규 구현 빈 등록 + all-new 경로 AC-1·AC-2 (AllNewModeTest 4개)
#    세 모듈이 모두 전환될 때까지 이 테스트는 RED 입니다.
./gradlew test --tests 'kr.elice.library.acceptance.AllNewModeTest'
```

`AllNewModeTest` 에서 확인하는 것:
- `allNewBeansRegistered`: `newBookService`·`newMemberService`·`newLoanService` 빈이 모두 등록됐는지
- `newLoanUsesCatalogRouter`: NewLoanService → CatalogRouter → NewBook/MemberService 크로스모듈 경로가 동작하는지
- `ac1_loanLimitEnforcedByNewImpl`: 신규 구현에서도 한도 5권이 지켜지는지
- `ac2_overdueBlocksEnforcedByNewImpl`: 신규 구현에서도 연체 거부가 지켜지는지

세 단계 확인이 모두 GREEN 이면 strangler 전환이 완료된 것입니다.

## 멱등 재실행

```bash
./lab.sh reset           # 다시 시작 상태(전부 legacy, springboot 비움)
```

reset → 세 발화 → verify 를 몇 번 반복해도 매번 3/3 전환 + 수용기준 green 으로 수렴합니다.
수용기준 테스트(`src/test`)가 고정된 채점기라, 구현 코드가 조금씩 달라도 같은 규칙을 통과합니다.
