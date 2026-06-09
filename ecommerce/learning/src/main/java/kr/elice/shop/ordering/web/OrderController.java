package kr.elice.shop.ordering.web;

import java.util.List;
import kr.elice.shop.ordering.application.OrderService;
import kr.elice.shop.ordering.domain.Order;
import kr.elice.shop.ordering.domain.OrderStatus;
import kr.elice.shop.shared.Page;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/**
 * 주문 REST 표면입니다. 목록·단건·이행을 노출합니다. 취소는 예약 해제·결제 환불 보상이 필요해
 * checkout 컨텍스트의 컨트롤러가 맡습니다(단방향 의존 유지).
 */
@RestController
@RequestMapping("/api/orders")
public class OrderController {

    private final OrderService orders;

    public OrderController(OrderService orders) {
        this.orders = orders;
    }

    @GetMapping
    public Page<OrderResponse> list(
            @RequestParam(required = false) String status,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int size) {
        OrderStatus filter = status == null ? null : OrderStatus.valueOf(status);
        Page<Order> found = orders.list(filter, page, size);
        List<OrderResponse> items = found.items().stream().map(OrderResponse::from).toList();
        return new Page<>(items, found.total(), found.page(), found.size(), found.pages());
    }

    @GetMapping("/{id}")
    public OrderResponse get(@PathVariable String id) {
        return OrderResponse.from(orders.get(id));
    }

    @PostMapping("/{id}/fulfill")
    public OrderResponse fulfill(@PathVariable String id) {
        return OrderResponse.from(orders.fulfill(id));
    }
}
