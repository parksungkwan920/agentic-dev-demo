# 04_verify · proof 증빙

> **생성기 산출물입니다.** `gen_proof_evidence.py` 가 Gradle JUnit XML 에서 자동 생성했습니다.
> 이 파일은 'SDD가 코드로 통과시켰다'의 공식 증거입니다. 손으로 수정하지 않습니다.

## 요약

```
BUILD SUCCESSFUL
total tests = 23 · passed = 23 · failed = 0 · errors = 0
ProductTest           4/4
ShopE2ETest           9/9
InventoryServiceTest  5/5
OrderTest             5/5
```

## E2E 시나리오 (9개)

| 테스트 이름 | 결과 |
| --- | --- |
| E2E-6 멱등성: 같은 키의 체크아웃·결제는 한 번만 반영된다 | ✅ PASS |
| E2E-2 결제 전 취소: 예약이 풀려 가용 재고가 복원된다 | ✅ PASS |
| E2E-9 결제 거절: declined 수단은 402 로 거부되고 주문은 CREATED 로 남는다 | ✅ PASS |
| E2E-3 결제 후 취소: 결제가 환불되고 재고가 복원된다 | ✅ PASS |
| E2E-8 이행 가드: 결제 전 주문은 이행이 거부된다 | ✅ PASS |
| E2E-5 검색·페이징: 이름 검색과 페이지 크기가 동작한다 | ✅ PASS |
| E2E-4 oversell 방지: 가용분을 넘는 두 번째 체크아웃은 거부된다 | ✅ PASS |
| E2E-7 아카이브 차단: ARCHIVED 상품은 장바구니에 담을 수 없다 | ✅ PASS |
| E2E-1 전체 여정: 상품 → 장바구니 → 체크아웃 → 결제 → 이행 | ✅ PASS |

## 단위 테스트 (14개)

| 클래스 | 통과 | 실패 |
| --- | --- | --- |
| ProductTest | 4 | 0 |
| InventoryServiceTest | 5 | 0 |
| OrderTest | 5 | 0 |

## 게이트 판정

- 테스트 게이트: `./gradlew test` → **BUILD SUCCESSFUL**
- 전체 23개 중 23개 통과, 0개 실패.

> **통과** — 모든 AC 가 JUnit 으로 검증되었습니다.
