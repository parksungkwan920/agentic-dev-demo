package kr.elice.shop.ordering.web;

import java.util.List;
import kr.elice.shop.ordering.domain.Order;

/** 주문 응답 DTO 입니다. 상태·총액과 함께 가격 스냅샷 라인을 내보냅니다. */
public record OrderResponse(
        String id, String status, long totalAmount, String paymentId, List<Line> lines) {

    public record Line(String productId, String name, long unitPrice, int quantity, long subtotal) {}

    public static OrderResponse from(Order order) {
        List<Line> lines = order.lines().stream()
                .map(l -> new Line(
                        l.productId(),
                        l.name(),
                        l.unitPrice().amount(),
                        l.quantity(),
                        l.subtotal().amount()))
                .toList();
        return new OrderResponse(
                order.id(),
                order.status().name(),
                order.totalAmount().amount(),
                order.paymentId(),
                lines);
    }
}
