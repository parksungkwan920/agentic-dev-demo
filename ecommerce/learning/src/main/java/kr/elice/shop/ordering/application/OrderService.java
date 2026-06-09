package kr.elice.shop.ordering.application;

import java.util.List;
import kr.elice.shop.ordering.domain.Order;
import kr.elice.shop.ordering.domain.OrderRepository;
import kr.elice.shop.ordering.domain.OrderStatus;
import kr.elice.shop.shared.DomainException;
import kr.elice.shop.shared.ErrorCode;
import kr.elice.shop.shared.Page;
import org.springframework.stereotype.Service;

/**
 * 주문 응용 서비스입니다. 조회·목록·이행을 담당합니다. 주문 생성과 취소 보상은 여러 컨텍스트를
 * 가로지르므로 checkout 오케스트레이션이 맡고, 이 서비스는 ordering 컨텍스트 안에서만 동작합니다.
 */
@Service
public class OrderService {

    private final OrderRepository orders;

    public OrderService(OrderRepository orders) {
        this.orders = orders;
    }

    /** id 로 주문을 찾습니다. 없으면 NOT_FOUND 로 거부합니다. */
    public Order get(String id) {
        return orders.findById(id)
                .orElseThrow(() -> new DomainException(ErrorCode.NOT_FOUND, "주문을 찾을 수 없습니다: " + id));
    }

    /** 상태 필터·페이징을 적용해 주문 목록을 돌려줍니다. */
    public Page<Order> list(OrderStatus status, int page, int size) {
        List<Order> matched = orders.findAll().stream()
                .filter(o -> status == null || o.status() == status)
                .toList();
        return Page.of(matched, page, size);
    }

    /** 주문을 이행합니다. 결제 전 주문은 PAYMENT_REQUIRED 로 거부합니다. */
    public Order fulfill(String id) {
        Order order = get(id);
        order.fulfill();
        return orders.save(order);
    }
}
