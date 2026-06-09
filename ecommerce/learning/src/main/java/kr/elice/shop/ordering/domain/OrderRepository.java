package kr.elice.shop.ordering.domain;

import java.util.List;
import java.util.Optional;

/** 주문 저장소 포트입니다. 멱등 키 매핑으로 같은 체크아웃이 주문을 두 번 만들지 않게 합니다. */
public interface OrderRepository {

    /** 주문을 저장하고 저장된 인스턴스를 돌려줍니다. */
    Order save(Order order);

    /** id 로 주문을 찾습니다. */
    Optional<Order> findById(String id);

    /** 모든 주문을 등록 순서대로 돌려줍니다. */
    List<Order> findAll();

    /** 멱등 키로 이전에 만든 주문을 찾습니다. */
    Optional<Order> findByIdempotencyKey(String key);

    /** 멱등 키와 주문 id 의 매핑을 기억합니다. */
    void rememberIdempotency(String key, String orderId);
}
