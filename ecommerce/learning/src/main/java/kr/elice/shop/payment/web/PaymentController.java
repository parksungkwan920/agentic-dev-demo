package kr.elice.shop.payment.web;

import kr.elice.shop.payment.application.PaymentService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/** 결제 REST 표면입니다. 결제·단건 조회·환불을 노출합니다. */
@RestController
@RequestMapping("/api/payments")
public class PaymentController {

    private final PaymentService payments;

    public PaymentController(PaymentService payments) {
        this.payments = payments;
    }

    public record PayRequest(String orderId, String method) {}

    @PostMapping
    public ResponseEntity<PaymentResponse> pay(
            @RequestBody PayRequest req,
            @RequestHeader(value = "Idempotency-Key", required = false) String idempotencyKey) {
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(PaymentResponse.from(payments.pay(req.orderId(), req.method(), idempotencyKey)));
    }

    @GetMapping("/{id}")
    public PaymentResponse get(@PathVariable String id) {
        return PaymentResponse.from(payments.get(id));
    }

    @PostMapping("/{id}/refund")
    public PaymentResponse refund(@PathVariable String id) {
        return PaymentResponse.from(payments.refund(id));
    }
}
