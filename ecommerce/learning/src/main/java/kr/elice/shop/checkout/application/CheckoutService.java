package kr.elice.shop.checkout.application;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import kr.elice.shop.cart.application.CartService;
import kr.elice.shop.cart.domain.Cart;
import kr.elice.shop.catalog.application.CatalogService;
import kr.elice.shop.inventory.application.InventoryService;
import kr.elice.shop.inventory.domain.Reservation;
import kr.elice.shop.ordering.domain.Order;
import kr.elice.shop.ordering.domain.OrderLine;
import kr.elice.shop.ordering.domain.OrderRepository;
import kr.elice.shop.payment.application.PaymentService;
import kr.elice.shop.shared.DomainException;
import kr.elice.shop.shared.Money;
import org.springframework.stereotype.Service;

/**
 * 체크아웃·취소 오케스트레이션 서비스입니다. 장바구니 → 예약 → 주문 흐름을 묶고, 중간에 실패하면
 * 잡아 둔 예약을 모두 풀어 보상합니다. 취소는 예약 해제 + 결제 환불 보상을 담당합니다.
 * 의존 방향: checkout → cart·catalog·inventory·ordering·payment (단방향).
 */
@Service
public class CheckoutService {

    private final CartService carts;
    private final CatalogService catalog;
    private final InventoryService inventory;
    private final OrderRepository orders;
    private final PaymentService payments;

    public CheckoutService(
            CartService carts,
            CatalogService catalog,
            InventoryService inventory,
            OrderRepository orders,
            PaymentService payments) {
        this.carts = carts;
        this.catalog = catalog;
        this.inventory = inventory;
        this.orders = orders;
        this.payments = payments;
    }

    /**
     * 장바구니를 체크아웃합니다. 멱등 키가 있고 이미 처리된 키라면 기존 주문을 돌려줍니다.
     * 예약 도중 재고가 부족하면 잡아 둔 예약을 모두 풀고 거부합니다.
     */
    public Order checkout(String cartId, String idempotencyKey) {
        if (idempotencyKey != null && !idempotencyKey.isBlank()) {
            var existing = orders.findByIdempotencyKey(idempotencyKey);
            if (existing.isPresent()) {
                return existing.get();
            }
        }

        Cart cart = carts.get(cartId);
        Map<String, Integer> items = cart.items();

        List<Reservation> reserved = new ArrayList<>();
        List<OrderLine> lines = new ArrayList<>();

        try {
            for (Map.Entry<String, Integer> entry : items.entrySet()) {
                String productId = entry.getKey();
                int qty = entry.getValue();
                Reservation r = inventory.reserve(productId, qty);
                reserved.add(r);

                var product = catalog.get(productId);
                lines.add(new OrderLine(productId, product.name(), product.price(), qty));
            }
        } catch (DomainException e) {
            // 일부 예약이 성공한 상태에서 실패 — 보상 해제
            for (Reservation r : reserved) {
                try {
                    inventory.release(r.id());
                } catch (Exception ignored) {
                    // 보상은 best-effort
                }
            }
            throw e;
        }

        List<String> reservationIds = reserved.stream().map(Reservation::id).toList();
        String orderId = "ord_" + UUID.randomUUID().toString().substring(0, 8);
        Order order = Order.create(orderId, lines, reservationIds);
        orders.save(order);

        if (idempotencyKey != null && !idempotencyKey.isBlank()) {
            orders.rememberIdempotency(idempotencyKey, orderId);
        }
        return order;
    }

    /**
     * 주문을 취소합니다. 주문이 PAID 였으면 결제를 환불하고, 예약을 모두 되돌립니다.
     * 취소 엔드포인트를 ordering 컨텍스트에 두지 않고 checkout 에 두는 이유는 의존 방향입니다.
     * ordering 이 payment 를 참조하면 순환이 생기므로, 모든 컨텍스트를 아는 checkout 이 담당합니다.
     */
    public Order cancel(String orderId) {
        Order order = orders.findById(orderId)
                .orElseThrow(() -> new kr.elice.shop.shared.DomainException(
                        kr.elice.shop.shared.ErrorCode.NOT_FOUND, "주문을 찾을 수 없습니다: " + orderId));

        boolean needsRefund = order.cancel();
        orders.save(order);

        if (needsRefund) {
            payments.refundForOrder(orderId);
        }

        for (String reservationId : order.reservationIds()) {
            try {
                inventory.cancel(reservationId);
            } catch (Exception ignored) {
                // 보상은 best-effort
            }
        }

        return order;
    }
}
