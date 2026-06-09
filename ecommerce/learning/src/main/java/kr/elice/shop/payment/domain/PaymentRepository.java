package kr.elice.shop.payment.domain;

import java.util.Optional;

/** 결제 저장소 포트입니다. 멱등 키 매핑으로 같은 결제 요청이 두 번 청구되지 않게 합니다. */
public interface PaymentRepository {

    /** 결제를 저장하고 저장된 인스턴스를 돌려줍니다. */
    Payment save(Payment payment);

    /** id 로 결제를 찾습니다. */
    Optional<Payment> findById(String id);

    /** 주문 id 로 결제를 찾습니다. 취소 보상 시 어떤 결제를 환불할지 찾는 데 씁니다. */
    Optional<Payment> findByOrderId(String orderId);

    /** 멱등 키로 이전 결제를 찾습니다. */
    Optional<Payment> findByIdempotencyKey(String key);

    /** 멱등 키와 결제 id 의 매핑을 기억합니다. */
    void rememberIdempotency(String key, String paymentId);
}
