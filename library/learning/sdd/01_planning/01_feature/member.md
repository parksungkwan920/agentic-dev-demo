# 01_planning · 회원(Member) 모듈 스펙

> **생성기 산출물입니다.** `gen_strangler_spec.py` 가 레거시 소스에서 자동 생성했습니다.
> 학습자·에이전트는 이 스펙으로 `springboot/NewMemberService` 를 구현합니다.

## 모듈 요약

회원 등록·단건 조회를 제공합니다. 도서 모듈과 마찬가지로 독립적이라 전환 2순위입니다.

## 추출된 퍼블릭 메서드

- `register()`
- `get()`

## 오류 코드

- `NOT_FOUND`

## EARS 수용기준

| AC | EARS | 검증 |
| --- | --- | --- |
| AC-M1 | 회원 등록 요청이 올 때, 시스템은 식별자와 이름을 가진 회원을 생성한다. | MemberControllerTest |
| AC-M2 | 없는 식별자로 조회하면, 시스템은 NOT_FOUND 로 거부한다. | MemberControllerTest |

## 구현 규약

- 클래스 이름: `NewMemberService`
- 패키지: `kr.elice.library.springboot`
- 인터페이스: `kr.elice.library.api.MemberService` 구현
- 저장소: 공유 `MemberStore` 사용
- 빈 이름: 스프링 기본 이름 `newMemberService`
