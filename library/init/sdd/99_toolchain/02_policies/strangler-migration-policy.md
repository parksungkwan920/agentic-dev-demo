# strangler 전환 정책 (toolchain · 정책)

> **toolchain 세 갈래 중 '정책' 역할을 담당합니다.** 사람이 바뀌어도 같은 방식으로
> 전환이 이뤄지도록 규칙을 글로 못 박아 둡니다. 에이전트·학습자 모두 이 정책을 따릅니다.

## 1. 전환 순서 규칙

도서 → 회원 → 대출 순서로 전환합니다. 이 순서는 의존성에서 나옵니다.

- **도서**: 의존 없음. 가장 먼저 전환합니다.
- **회원**: 의존 없음. 두 번째로 전환합니다.
- **대출**: 도서·회원에 의존. 반드시 마지막에 전환합니다.
- 이 순서를 어기면 전환 중에 대출이 아직 레거시인 도서·회원을 찾지 못합니다.

## 2. 클래스 이름 규약

| 모듈 | 클래스 이름 | 빈 이름 (스프링 기본) |
|---|---|---|
| 도서 | `NewBookService` | `newBookService` |
| 회원 | `NewMemberService` | `newMemberService` |
| 대출 | `NewLoanService` | `newLoanService` |

- 이름이 다르면 라우터(`CatalogRouter`, `LoanRouter`)가 빈을 찾지 못합니다.
- 클래스 이름을 규약대로 쓰면 스프링이 자동으로 `new{Kind}Service` 빈 이름을 부여합니다.

## 3. 패키지 위치

모든 신규 구현은 `src/main/java/kr/elice/library/springboot/` 에 둡니다.

- `legacy/` 패키지는 시작 코드 보존 용도입니다. 수정하지 않습니다.
- `springboot/` 에 구현이 없는데 `migration.properties` 를 `new` 로 바꾸면 라우터가 실패합니다.
- `run_strangler_check.py` 가 이 불일치를 사전에 잡아냅니다.

## 4. 대출 모듈의 CatalogRouter 의무 사용

`NewLoanService` 는 도서·회원을 **반드시 `CatalogRouter` 를 통해** 호출해야 합니다.

```java
// 옳음: CatalogRouter 로 활성 구현을 받아 호출합니다
catalog.members().get(memberId);
catalog.books().get(bookId);

// 틀림: 레거시를 직접 호출하면 전환 중간 상태에서 끊깁니다
members.get(memberId);  // LegacyMemberService 직접 참조 금지
```

`CatalogRouter` 를 쓰면 도서·회원이 아직 레거시여도 대출이 정상 동작합니다.

## 5. migration.properties 변경 시점

구현 파일이 `springboot/` 에 실제로 존재할 때만 해당 모듈을 `new` 로 바꿉니다.

```properties
# 도서 전환 완료 후 → module.books=new (회원·대출은 legacy 유지)
# 회원 전환 완료 후 → module.members=new
# 대출 전환 완료 후 → module.loans=new
```

## 6. 검증 게이트 순서

모든 전환 단계에서 아래 게이트를 순서대로 통과해야 완료입니다.

1. **구조 게이트**: `python3 sdd/99_toolchain/01_automation/run_strangler_check.py`
   - 전환 진행 상태와 구현 일관성을 판정합니다.
2. **행위 게이트**: `./gradlew test`
   - 수용기준 AC-1·AC-2 포함 전체가 green 이어야 합니다.
3. **완료 게이트** (세 모듈 전환 후): `./gradlew test --tests '...AllNewModeTest'`
   - 빈 등록·크로스모듈·AC-1·AC-2 를 all-new 경로로 검증합니다.

게이트 실패 시 다음 단계로 넘어가지 않습니다.

## 7. 공유 저장소 사용

레거시와 신규 구현은 같은 저장소(`BookStore`, `MemberStore`, `LoanStore`)를 씁니다.

- 전환 중간 상태에서도 레거시와 새 구현이 같은 데이터를 봅니다.
- 이것이 스트랭글러 패턴에서 '공유 DB 역할'을 하는 장치입니다.
