package kr.elice.shop.catalog.domain;

import java.util.List;
import java.util.Optional;

/**
 * 상품 저장소 포트입니다. 도메인은 이 인터페이스에만 의존하고, 실제 저장 방식(인메모리·JPA)은
 * infrastructure 어댑터가 결정합니다. 멱등 키 매핑도 저장소가 함께 책임집니다.
 */
public interface ProductRepository {

    /** 상품을 저장하고 저장된 인스턴스를 돌려줍니다. */
    Product save(Product product);

    /** id 로 상품을 찾습니다. */
    Optional<Product> findById(String id);

    /** 모든 상품을 등록 순서대로 돌려줍니다. */
    List<Product> findAll();

    /** 멱등 키로 이전에 등록한 상품을 찾습니다. */
    Optional<Product> findByIdempotencyKey(String key);

    /** 멱등 키와 상품 id 의 매핑을 기억합니다. */
    void rememberIdempotency(String key, String productId);
}
