package kr.elice.shop.ordering.infrastructure;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import kr.elice.shop.ordering.domain.Order;
import kr.elice.shop.ordering.domain.OrderRepository;
import org.springframework.stereotype.Repository;

/** 주문 저장소의 인메모리 어댑터입니다. 등록 순서를 유지하고 멱등 키 매핑을 함께 보관합니다. */
@Repository
public class InMemoryOrderRepository implements OrderRepository {

    private final Map<String, Order> byId = new LinkedHashMap<>();
    private final Map<String, String> idempotency = new ConcurrentHashMap<>();

    @Override
    public synchronized Order save(Order order) {
        byId.put(order.id(), order);
        return order;
    }

    @Override
    public synchronized Optional<Order> findById(String id) {
        return Optional.ofNullable(byId.get(id));
    }

    @Override
    public synchronized List<Order> findAll() {
        return new ArrayList<>(byId.values());
    }

    @Override
    public Optional<Order> findByIdempotencyKey(String key) {
        String id = idempotency.get(key);
        return id == null ? Optional.empty() : findById(id);
    }

    @Override
    public void rememberIdempotency(String key, String orderId) {
        idempotency.put(key, orderId);
    }
}
