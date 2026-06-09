package kr.elice.shop.payment.application;

import java.util.UUID;
import kr.elice.shop.inventory.application.InventoryService;
import kr.elice.shop.ordering.domain.Order;
import kr.elice.shop.ordering.domain.OrderRepository;
import kr.elice.shop.payment.domain.Payment;
import kr.elice.shop.payment.domain.PaymentGateway;
import kr.elice.shop.payment.domain.PaymentRepository;
import kr.elice.shop.shared.DomainException;
import kr.elice.shop.shared.ErrorCode;
import org.springframework.stereotype.Service;

/**
 * 결제 응용 서비스입니다. 게이트웨이 승인 → 예약 확정 → 주문 PAID 전환을 한 흐름으로 묶습니다.
 * 같은 멱등 키 재요청은 기존 결제를 그대로 돌려줘 두 번 청구하지 않습니다. 거절되면 주문은 CREATED 로
 * 남고 PAYMENT_DECLINED 로 거부합니다.
 */
@Service
public class PaymentService {

    private final PaymentRepository payments;
    private final PaymentGateway gateway;
    private final OrderRepository orders;
    private final InventoryService inventory;

    public PaymentService(
            PaymentRepository payments,
            PaymentGateway gateway,
            OrderRepository orders,
            InventoryService inventory) {
        this.payments = payments;
        this.gateway = gateway;
        this.orders = orders;
        this.inventory = inventory;
    }

    /** 주문을 결제합니다. 승인되면 예약을 확정하고 주문을 PAID 로 전환합니다. */
    public Payment pay(String orderId, String method, String idempotencyKey) {
        if (idempotencyKey != null && !idempotencyKey.isBlank()) {
            var existing = payments.findByIdempotencyKey(idempotencyKey);
            if (existing.isPresent()) {
                return existing.get();
            }
        }
        Order order = orders.findById(orderId)
                .orElseThrow(() -> new DomainException(ErrorCode.NOT_FOUND, "주문을 찾을 수 없습니다: " + orderId));

        boolean approved = gateway.charge(orderId, method, order.totalAmount());
        if (!approved) {
            throw new DomainException(ErrorCode.PAYMENT_DECLINED, "결제가 거절되었습니다");
        }

        String id = "pay_" + UUID.randomUUID().toString().substring(0, 8);
        Payment payment = Payment.capture(id, orderId, method, order.totalAmount());
        payments.save(payment);

        for (String reservationId : order.reservationIds()) {
            inventory.confirm(reservationId);
        }
        order.markPaid(id);
        orders.save(order);

        if (idempotencyKey != null && !idempotencyKey.isBlank()) {
            payments.rememberIdempotency(idempotencyKey, id);
        }
        return payment;
    }

    /** id 로 결제를 찾습니다. 없으면 NOT_FOUND 로 거부합니다. */
    public Payment get(String id) {
        return payments.findById(id)
                .orElseThrow(() -> new DomainException(ErrorCode.NOT_FOUND, "결제를 찾을 수 없습니다: " + id));
    }

    /** 결제를 환불합니다. */
    public Payment refund(String id) {
        Payment payment = get(id);
        payment.refund();
        return payments.save(payment);
    }

    /** 주문에 연결된 결제를 환불합니다. 취소 보상에서 호출합니다. 결제가 없으면 아무것도 하지 않습니다. */
    public void refundForOrder(String orderId) {
        payments.findByOrderId(orderId).ifPresent(p -> {
            p.refund();
            payments.save(p);
        });
    }
}
