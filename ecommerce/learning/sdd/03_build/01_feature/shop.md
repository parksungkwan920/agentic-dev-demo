# 03_build · 이커머스 쇼핑 current-state

> build 단계가 끝난 현재 구현 상태를 기록합니다. 각 컨텍스트는 domain·application·
> infrastructure·web 네 레이어로 분리되어 있습니다. 이 지도는 다음 작업자가 코드를
> 다시 읽지 않고도 무엇이 어디에 있는지 알 수 있게 합니다.
>
> 아래 "API 표면"과 "모듈 구조"는 완성본(reference target)을 기술합니다. 이 learning
> 워크스페이스의 실제 진행 현황은 바로 아래 "현재 구현 현황" 절에 정직하게 분리해 기록합니다.

## 현재 구현 현황 (learning 워크스페이스 · STEP 2)

STEP 2 에서는 shop_todos.md 의 도메인 구역을 구현했습니다. 현재 실제로 소스에 존재하는 범위는 다음과 같습니다.

- 공유 커널(shared)을 구현했습니다. `Money`, `ErrorCode`, `DomainException`, `Page` 가 존재합니다.
- catalog 컨텍스트의 도메인·인프라·응용을 구현했습니다. `Product`, `ProductStatus`, `ProductRepository`(port), `InMemoryProductRepository`, `CatalogService` 가 존재합니다.
- inventory 컨텍스트의 도메인·인프라·응용을 구현했습니다. `Reservation`, `ReservationStatus`, `ReservationRepository`(port), `InMemoryReservationRepository`, `InventoryService` 가 존재합니다. reserve 는 synchronized 로 직렬화해 동시 예약 oversell 을 막습니다.
- ordering 컨텍스트의 도메인을 구현했습니다. `Order`, `OrderLine`, `OrderStatus`, `OrderRepository`(port) 가 존재합니다.
- cart 컨텍스트의 도메인을 구현했습니다. `Cart`, `CartRepository`(port) 가 존재합니다.
- payment 컨텍스트의 도메인을 구현했습니다. `Payment`, `PaymentStatus`, `PaymentGateway`(port), `PaymentRepository`(port) 가 존재합니다.

아직 구현하지 않은(다음 빌드 청크) 범위는 다음과 같습니다.

- 모든 컨텍스트의 web 계층(컨트롤러·DTO·전역 예외 핸들러)을 아직 만들지 않았습니다.
- cart·ordering·payment 의 응용 서비스와 인메모리 어댑터를 아직 만들지 않았습니다.
- checkout 오케스트레이션(체크아웃·취소 보상)을 아직 만들지 않았습니다.
- `ShopApplication` 진입점과 `DemoPaymentGateway` 어댑터를 아직 만들지 않았습니다.
- 그래서 E2E 9개는 아직 실행 대상이 아닙니다. 14개 도메인 단위 테스트만 green 입니다.

검증 증거는 `04_verify/01_feature/shop.md` 의 "STEP 2 검증" 절을 참고합니다.

## 모듈 구조 (모놀리식 · DDD)

```
src/main/java/kr/elice/shop
├── ShopApplication.java          애플리케이션 진입점
├── shared/                       Money · ErrorCode · DomainException · Page · ApiExceptionHandler
├── catalog/                      상품 카탈로그
│   ├── domain/                   Product · ProductStatus · ProductRepository(port)
│   ├── application/              CatalogService
│   ├── infrastructure/           InMemoryProductRepository
│   └── web/                      ProductController · ProductResponse
├── inventory/                    재고 예약
│   ├── domain/                   Reservation · ReservationStatus · ReservationRepository(port)
│   ├── application/              InventoryService
│   ├── infrastructure/           InMemoryReservationRepository
│   └── web/                      InventoryController
├── cart/                         장바구니
│   ├── domain/                   Cart · CartRepository(port)
│   ├── application/              CartService
│   ├── infrastructure/           InMemoryCartRepository
│   └── web/                      CartController · CartView
├── ordering/                     주문 상태머신
│   ├── domain/                   Order · OrderLine · OrderStatus · OrderRepository(port)
│   ├── application/              OrderService
│   ├── infrastructure/           InMemoryOrderRepository
│   └── web/                      OrderController · OrderResponse
├── payment/                      결제·환불
│   ├── domain/                   Payment · PaymentStatus · PaymentGateway(port) · PaymentRepository(port)
│   ├── application/              PaymentService
│   ├── infrastructure/           InMemoryPaymentRepository · DemoPaymentGateway
│   └── web/                      PaymentController · PaymentResponse
└── checkout/                     오케스트레이션
    ├── application/              CheckoutService (체크아웃 + 취소 보상)
    └── web/                      CheckoutController
```

## API 표면

| 메서드 | 경로 | 설명 |
| --- | --- | --- |
| POST | /api/products | 상품 등록 (Idempotency-Key) |
| GET | /api/products | 검색·상태필터·페이징 목록 |
| GET | /api/products/{id} | 상품 단건 |
| POST | /api/products/{id}/stock-additions | 재고 추가 |
| POST | /api/products/{id}/stock-reductions | 재고 차감 |
| POST | /api/products/{id}/archive | 아카이브 |
| GET | /api/inventory/{productId} | 가용 재고 조회 |
| POST | /api/carts | 장바구니 생성 |
| GET | /api/carts/{id} | 장바구니 조회 (총액 계산) |
| POST | /api/carts/{id}/items | 상품 담기 |
| PATCH | /api/carts/{id}/items/{productId} | 수량 변경 |
| DELETE | /api/carts/{id}/items/{productId} | 항목 삭제 |
| POST | /api/carts/{id}/clear | 비우기 |
| POST | /api/checkout | 체크아웃 (Idempotency-Key) |
| GET | /api/orders | 주문 목록 (상태필터·페이징) |
| GET | /api/orders/{id} | 주문 단건 |
| POST | /api/orders/{id}/fulfill | 이행 |
| POST | /api/orders/{id}/cancel | 취소 (예약 해제 + 환불 보상) |
| POST | /api/payments | 결제 (Idempotency-Key) |
| GET | /api/payments/{id} | 결제 단건 |
| POST | /api/payments/{id}/refund | 환불 |

## 설계 메모

- 모든 비즈니스 규칙은 애그리거트(Product·Reservation·Cart·Order·Payment) 안에 모여 있습니다. 서비스는 흐름을 조율하고 저장소와 연결합니다.
- 저장소는 포트 인터페이스로 추상화되어 인메모리 어댑터로 동작합니다. 운영에서는 JPA 어댑터로 교체합니다.
- 컨텍스트 간 결합은 단방향입니다. inventory·cart 는 catalog 에, payment 는 ordering·inventory 에, checkout 은 전부에 의존합니다. 순환 의존이 없습니다.
- 가격은 주문 시점에 OrderLine 으로 스냅샷되어 이후 상품 가격 변동과 무관하게 고정됩니다.
