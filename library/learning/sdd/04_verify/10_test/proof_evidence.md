# 04_verify · proof 증빙

> **생성기 산출물입니다.** `gen_proof_evidence.py` 가 Gradle JUnit XML 에서 자동 생성했습니다.
> 이 파일은 'SDD가 코드로 통과시켰다'의 공식 증거입니다. 손으로 수정하지 않습니다.

## 요약

```
BUILD FAILED
total tests = 7 · passed = 3 · failed = 4 · errors = 0
AllNewModeTest        0/4
LibraryAcceptanceTest 3/3
```

## E2E 시나리오 (3개)

| 테스트 이름 | 결과 |
| --- | --- |
| 정상 흐름: 회원·도서를 만들고 대출·반납이 동작한다 | ✅ PASS |
| AC-1: 대출 한도 5권을 넘기면 여섯 번째 대출이 거부된다 | ✅ PASS |
| AC-2: 연체 중인 회원은 새 대출이 거부된다 | ✅ PASS |

## 단위 테스트 (4개)

| 클래스 | 통과 | 실패 |
| --- | --- | --- |
| AllNewModeTest | 0 | 4 |

## 게이트 판정

- 테스트 게이트: `./gradlew test` → **BUILD FAILED**
- 전체 7개 중 3개 통과, 4개 실패.

> **실패** — 실패한 케이스를 수정한 뒤 다시 실행합니다.
