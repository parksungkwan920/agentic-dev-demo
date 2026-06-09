package kr.elice.shop.catalog.application;

import java.util.List;
import java.util.UUID;
import kr.elice.shop.catalog.domain.Product;
import kr.elice.shop.catalog.domain.ProductRepository;
import kr.elice.shop.catalog.domain.ProductStatus;
import kr.elice.shop.shared.DomainException;
import kr.elice.shop.shared.ErrorCode;
import kr.elice.shop.shared.Money;
import kr.elice.shop.shared.Page;
import org.springframework.stereotype.Service;

/**
 * 상품 카탈로그 응용 서비스입니다. 등록(멱등)·조회·검색/페이징·재고가감·아카이브 흐름을 조율하고,
 * 비즈니스 규칙 자체는 Product 애그리거트에 위임합니다.
 */
@Service
public class CatalogService {

    private final ProductRepository repository;

    public CatalogService(ProductRepository repository) {
        this.repository = repository;
    }

    /**
     * 상품을 등록합니다. 멱등 키가 주어지고 같은 키로 이미 등록했다면 기존 상품을 그대로 돌려줍니다.
     */
    public Product create(String name, long price, int initialStock, String idempotencyKey) {
        if (idempotencyKey != null && !idempotencyKey.isBlank()) {
            var existing = repository.findByIdempotencyKey(idempotencyKey);
            if (existing.isPresent()) {
                return existing.get();
            }
        }
        String id = "prod_" + UUID.randomUUID().toString().substring(0, 8);
        Product product = Product.create(id, name, Money.won(price), initialStock);
        repository.save(product);
        if (idempotencyKey != null && !idempotencyKey.isBlank()) {
            repository.rememberIdempotency(idempotencyKey, id);
        }
        return product;
    }

    /** id 로 상품을 찾습니다. 없으면 NOT_FOUND 로 거부합니다. */
    public Product get(String id) {
        return repository.findById(id)
                .orElseThrow(() -> new DomainException(ErrorCode.NOT_FOUND, "상품을 찾을 수 없습니다: " + id));
    }

    /** 재고를 더하고 저장된 상품을 돌려줍니다. */
    public Product addStock(String id, int quantity) {
        Product product = get(id);
        product.addStock(quantity);
        return repository.save(product);
    }

    /** 재고를 빼고 저장된 상품을 돌려줍니다. */
    public Product reduceStock(String id, int quantity) {
        Product product = get(id);
        product.reduceStock(quantity);
        return repository.save(product);
    }

    /** 상품을 아카이브하고 저장된 상품을 돌려줍니다. */
    public Product archive(String id) {
        Product product = get(id);
        product.archive();
        return repository.save(product);
    }

    /**
     * 이름 검색·상태 필터·페이징을 적용해 상품 목록을 돌려줍니다. query 가 비면 전체를 대상으로 합니다.
     */
    public Page<Product> search(String query, ProductStatus status, int page, int size) {
        List<Product> matched = repository.findAll().stream()
                .filter(p -> query == null || query.isBlank() || p.name().contains(query))
                .filter(p -> status == null || p.status() == status)
                .toList();
        return Page.of(matched, page, size);
    }
}
