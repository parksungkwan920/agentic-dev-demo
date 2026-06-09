package kr.elice.shop.catalog.infrastructure;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import kr.elice.shop.catalog.domain.Product;
import kr.elice.shop.catalog.domain.ProductRepository;
import org.springframework.stereotype.Repository;

/**
 * 상품 저장소의 인메모리 어댑터입니다. 등록 순서를 유지해 목록·페이징이 결정적으로 동작합니다.
 * 운영에서는 JPA 어댑터로 교체합니다.
 */
@Repository
public class InMemoryProductRepository implements ProductRepository {

    private final Map<String, Product> byId = new LinkedHashMap<>();
    private final Map<String, String> idempotency = new ConcurrentHashMap<>();

    @Override
    public synchronized Product save(Product product) {
        byId.put(product.id(), product);
        return product;
    }

    @Override
    public synchronized Optional<Product> findById(String id) {
        return Optional.ofNullable(byId.get(id));
    }

    @Override
    public synchronized List<Product> findAll() {
        return new ArrayList<>(byId.values());
    }

    @Override
    public Optional<Product> findByIdempotencyKey(String key) {
        String id = idempotency.get(key);
        return id == null ? Optional.empty() : findById(id);
    }

    @Override
    public void rememberIdempotency(String key, String productId) {
        idempotency.put(key, productId);
    }
}
