package kr.elice.shop.cart.domain;

import java.util.Optional;

/** 장바구니 저장소 포트입니다. */
public interface CartRepository {

    /** 장바구니를 저장하고 저장된 인스턴스를 돌려줍니다. */
    Cart save(Cart cart);

    /** id 로 장바구니를 찾습니다. */
    Optional<Cart> findById(String id);
}
