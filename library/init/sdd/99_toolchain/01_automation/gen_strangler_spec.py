# -*- coding: utf-8 -*-
"""생성기(generator): 레거시 소스와 요구사항에서 모듈별 SDD 스펙을 생성합니다.

toolchain 세 갈래 중 '생성기' 역할을 담당합니다. 사람이 레거시 코드를 읽고
손으로 스펙을 작성하는 대신, 이 스크립트가 레거시 Java 소스와 요구사항 원문을
분석해 sdd/01_planning/01_feature/ 아래에 모듈별 EARS 스펙 마크다운을 만듭니다.

생성된 스펙은 학습자와 에이전트가 springboot 신규 구현을 작성할 때 기준 문서로
사용합니다. 코드가 아니라 업무 규칙만 담으므로 프레임워크 의존 없이 재사용됩니다.

사용법:
    python3 sdd/99_toolchain/01_automation/gen_strangler_spec.py
    python3 sdd/99_toolchain/01_automation/gen_strangler_spec.py --dry-run
"""
import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
LEGACY_DIR = ROOT / "src/main/java/kr/elice/library/legacy"
OUT_DIR = ROOT / "sdd/01_planning/01_feature"
REQ_FILE = ROOT / "sdd/00_sources/02_requirements/legacy-library.md"


# ── 레거시 소스 파서 ──────────────────────────────────────────────────────────

def _public_methods(java_text: str) -> list[str]:
    """Java 소스에서 public 메서드 시그니처를 추출합니다."""
    pattern = re.compile(
        r"public\s+(?!class|interface|static|final)[\w<>\[\],\s]+\s+(\w+)\s*\([^)]*\)"
    )
    return [m.group(1) for m in pattern.finditer(java_text)]


def _exception_codes(java_text: str) -> list[str]:
    """LibraryException.Code 사용 목록을 추출합니다."""
    return re.findall(r"LibraryException\.Code\.(\w+)", java_text)


def _read_legacy(filename: str) -> str:
    path = LEGACY_DIR / filename
    return path.read_text(encoding="utf-8") if path.exists() else ""


# ── 스펙 생성기 ───────────────────────────────────────────────────────────────

def gen_book_spec() -> str:
    src = _read_legacy("LegacyBookService.java")
    methods = _public_methods(src)
    errors = _exception_codes(src)
    return f"""# 01_planning · 도서(Book) 모듈 스펙

> **생성기 산출물입니다.** `gen_strangler_spec.py` 가 레거시 소스에서 자동 생성했습니다.
> 학습자·에이전트는 이 스펙으로 `springboot/NewBookService` 를 구현합니다.

## 모듈 요약

도서 등록·단건 조회·목록 조회를 제공합니다. 다른 모듈에 의존하지 않아 전환 1순위입니다.

## 추출된 퍼블릭 메서드

{chr(10).join(f"- `{m}()`" for m in methods) or "- (없음)"}

## 오류 코드

{chr(10).join(f"- `{e}`" for e in errors) or "- (없음)"}

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
"""


def gen_member_spec() -> str:
    src = _read_legacy("LegacyMemberService.java")
    methods = _public_methods(src)
    errors = _exception_codes(src)
    return f"""# 01_planning · 회원(Member) 모듈 스펙

> **생성기 산출물입니다.** `gen_strangler_spec.py` 가 레거시 소스에서 자동 생성했습니다.
> 학습자·에이전트는 이 스펙으로 `springboot/NewMemberService` 를 구현합니다.

## 모듈 요약

회원 등록·단건 조회를 제공합니다. 도서 모듈과 마찬가지로 독립적이라 전환 2순위입니다.

## 추출된 퍼블릭 메서드

{chr(10).join(f"- `{m}()`" for m in methods) or "- (없음)"}

## 오류 코드

{chr(10).join(f"- `{e}`" for e in errors) or "- (없음)"}

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
"""


def gen_loan_spec() -> str:
    src = _read_legacy("LegacyLoanService.java")
    methods = _public_methods(src)
    errors = _exception_codes(src)
    return f"""# 01_planning · 대출(Loan) 모듈 스펙

> **생성기 산출물입니다.** `gen_strangler_spec.py` 가 레거시 소스에서 자동 생성했습니다.
> 학습자·에이전트는 이 스펙으로 `springboot/NewLoanService` 를 구현합니다.

## 모듈 요약

대출·반납을 제공하며, 도서와 회원에 의존합니다. 두 모듈 전환 후 마지막에 전환합니다.
업무 규칙 AC-1(한도 5권)·AC-2(연체 거부)가 이 모듈의 핵심 자산입니다.

## 추출된 퍼블릭 메서드

{chr(10).join(f"- `{m}()`" for m in methods) or "- (없음)"}

## 오류 코드

{chr(10).join(f"- `{e}`" for e in errors) or "- (없음)"}

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
"""


# ── 메인 ─────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="strangler 전환용 SDD 스펙 생성기")
    parser.add_argument("--dry-run", action="store_true", help="파일을 쓰지 않고 내용만 출력합니다")
    args = parser.parse_args()

    specs = {
        "book.md": gen_book_spec(),
        "member.md": gen_member_spec(),
        "loan.md": gen_loan_spec(),
    }

    if args.dry_run:
        for name, content in specs.items():
            print(f"\n{'='*60}\n# {name}\n{'='*60}")
            print(content[:500], "...(생략)")
        print("\n[dry-run] 실제 파일을 쓰지 않았습니다.")
        return 0

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, content in specs.items():
        path = OUT_DIR / name
        path.write_text(content, encoding="utf-8")
        print(f"  생성: {path.relative_to(ROOT)}")

    print(f"\n[gen_strangler_spec] {len(specs)}개 스펙 파일을 sdd/01_planning/01_feature/ 에 생성했습니다.")
    print("  다음 단계: 에이전트에게 이 스펙으로 springboot/New*Service 를 구현하도록 발화합니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
