package kr.elice.shop.payment.infrastructure;

import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import kr.elice.shop.payment.domain.Payment;
import kr.elice.shop.payment.domain.PaymentRepository;
import org.springframework.stereotype.Repository;

/** 결제 저장소의 인메모리 어댑터입니다. 주문별·멱등키별 조회를 위해 보조 색인을 함께 둡니다. */
@Repository
public class InMemoryPaymentRepository implements PaymentRepository {

    private final Map<String, Payment> byId = new ConcurrentHashMap<>();
    private final Map<String, String> byOrderId = new ConcurrentHashMap<>();
    private final Map<String, String> idempotency = new ConcurrentHashMap<>();

    @Override
    public Payment save(Payment payment) {
        byId.put(payment.id(), payment);
        byOrderId.put(payment.orderId(), payment.id());
        return payment;
    }

    @Override
    public Optional<Payment> findById(String id) {
        return Optional.ofNullable(byId.get(id));
    }

    @Override
    public Optional<Payment> findByOrderId(String orderId) {
        String id = byOrderId.get(orderId);
        return id == null ? Optional.empty() : findById(id);
    }

    @Override
    public Optional<Payment> findByIdempotencyKey(String key) {
        String id = idempotency.get(key);
        return id == null ? Optional.empty() : findById(id);
    }

    @Override
    public void rememberIdempotency(String key, String paymentId) {
        idempotency.put(key, paymentId);
    }
}
