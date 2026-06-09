package kr.elice.shop.checkout.web;

import kr.elice.shop.checkout.application.CheckoutService;
import kr.elice.shop.ordering.web.OrderResponse;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 체크아웃·취소 REST 표면입니다. 체크아웃과 주문 취소를 노출합니다. 취소를 ordering 컨트롤러가
 * 아닌 여기에 두는 이유는 보상 트랜잭션이 payment 를 참조해야 하기 때문입니다.
 */
@RestController
@RequestMapping
public class CheckoutController {

    private final CheckoutService checkout;

    public CheckoutController(CheckoutService checkout) {
        this.checkout = checkout;
    }

    public record CheckoutRequest(String cartId) {}

    @PostMapping("/api/checkout")
    public ResponseEntity<OrderResponse> checkout(
            @RequestBody CheckoutRequest req,
            @RequestHeader(value = "Idempotency-Key", required = false) String idempotencyKey) {
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(OrderResponse.from(checkout.checkout(req.cartId(), idempotencyKey)));
    }

    @PostMapping("/api/orders/{id}/cancel")
    public OrderResponse cancel(@PathVariable String id) {
        return OrderResponse.from(checkout.cancel(id));
    }
}
