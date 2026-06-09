package kr.elice.shop.cart.infrastructure;

import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import kr.elice.shop.cart.domain.Cart;
import kr.elice.shop.cart.domain.CartRepository;
import org.springframework.stereotype.Repository;

/** 장바구니 저장소의 인메모리 어댑터입니다. */
@Repository
public class InMemoryCartRepository implements CartRepository {

    private final Map<String, Cart> byId = new ConcurrentHashMap<>();

    @Override
    public Cart save(Cart cart) {
        byId.put(cart.id(), cart);
        return cart;
    }

    @Override
    public Optional<Cart> findById(String id) {
        return Optional.ofNullable(byId.get(id));
    }
}
