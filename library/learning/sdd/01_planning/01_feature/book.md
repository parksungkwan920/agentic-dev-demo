# 01_planning · 도서(Book) 모듈 스펙

> **생성기 산출물입니다.** `gen_strangler_spec.py` 가 레거시 소스에서 자동 생성했습니다.
> 학습자·에이전트는 이 스펙으로 `springboot/NewBookService` 를 구현합니다.

## 모듈 요약

도서 등록·단건 조회·목록 조회를 제공합니다. 다른 모듈에 의존하지 않아 전환 1순위입니다.

## 추출된 퍼블릭 메서드

- `register()`
- `get()`
- `list()`

## 오류 코드

- `NOT_FOUND`

## EARS 수용기준

| AC | EARS | 검증 |
| --- | --- | --- |
| AC-B1 | 도서 등록 요청이 올 때, 시스템은 식별자와 제목을 가진 도서를 생성한다. | BookControllerTest |
| AC-B2 | 없는 식별자로 조회하면, 시스템은 NOT_FOUND 로 거부한다. | BookControllerTest |
| AC-B3 | 목록 조회 요청이 올 때, 시스템은 등록된 도서 전체를 돌려준다. | BookControllerTest |

## 구현 규약

- 클래스 이름: `NewBookService`
- 패키지: `kr.elice.library.springboot`
- 인터페이스: `kr.elice.library.api.BookService` 구현
- 저장소: 공유 `BookStore` 사용 (레거시와 같은 데이터를 봅니다)
- 빈 이름: 스프링 기본 이름 `newBookService` (라우터가 자동 선택)
