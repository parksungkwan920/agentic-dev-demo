# 01_planning · 대출(Loan) 모듈 스펙

> **생성기 산출물입니다.** `gen_strangler_spec.py` 가 레거시 소스에서 자동 생성했습니다.
> 학습자·에이전트는 이 스펙으로 `springboot/NewLoanService` 를 구현합니다.

## 모듈 요약

대출·반납을 제공하며, 도서와 회원에 의존합니다. 두 모듈 전환 후 마지막에 전환합니다.
업무 규칙 AC-1(한도 5권)·AC-2(연체 거부)가 이 모듈의 핵심 자산입니다.

## 추출된 퍼블릭 메서드

- `borrow()`
- `giveBack()`
- `activeCount()`
- `hasOverdue()`

## 오류 코드

- `LOAN_LIMIT_EXCEEDED`
- `OVERDUE_EXISTS`
- `NOT_FOUND`

## EARS 수용기준 (업무 규칙)

| AC | EARS | 검증 |
| --- | --- | --- |
| AC-L1 | 대출 요청이 올 때, 시스템은 회원과 도서가 모두 존재하면 대출을 생성한다. | LibraryAcceptanceTest |
| AC-1 | 만약 활성 대출이 5건 이상이면, 시스템은 LOAN_LIMIT_EXCEEDED 로 거부한다. | LibraryAcceptanceTest.ac1_loanLimit |
| AC-2 | 만약 연체 중인 대출이 있으면, 시스템은 OVERDUE_EXISTS 로 거부한다. | LibraryAcceptanceTest.ac2_overdueBlocks |
| AC-L2 | 반납 요청이 올 때, 시스템은 해당 대출을 반납 처리해 활성에서 제외한다. | LibraryAcceptanceTest |

## 구현 규약 (중요)

- 클래스 이름: `NewLoanService`
- 패키지: `kr.elice.library.springboot`
- 인터페이스: `kr.elice.library.api.LoanService` 구현
- **도서·회원 호출: `platform.CatalogRouter` 를 통해 활성 구현을 받아 호출합니다.**
  레거시처럼 직접 부르면 전환 중간 상태에서 끊깁니다.
- 저장소: 공유 `LoanStore` 사용
- 빈 이름: 스프링 기본 이름 `newLoanService`
