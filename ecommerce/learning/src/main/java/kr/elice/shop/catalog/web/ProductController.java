package kr.elice.shop.catalog.web;

import java.util.List;
import kr.elice.shop.catalog.application.CatalogService;
import kr.elice.shop.catalog.domain.Product;
import kr.elice.shop.shared.Page;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/** 상품 REST 표면입니다. 등록·검색·단건·재고가감·아카이브를 노출합니다. */
@RestController
@RequestMapping("/api/products")
public class ProductController {

    private final CatalogService catalog;

    public ProductController(CatalogService catalog) {
        this.catalog = catalog;
    }

    public record CreateProductRequest(String name, long price, int initialStock) {}

    public record StockRequest(int quantity) {}

    @PostMapping
    public ResponseEntity<ProductResponse> create(
            @RequestBody CreateProductRequest req,
            @RequestHeader(value = "Idempotency-Key", required = false) String idempotencyKey) {
        Product product = catalog.create(req.name(), req.price(), req.initialStock(), idempotencyKey);
        return ResponseEntity.status(HttpStatus.CREATED).body(ProductResponse.from(product));
    }

    @GetMapping
    public Page<ProductResponse> list(
            @RequestParam(required = false) String q,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int size) {
        Page<Product> found = catalog.search(q, null, page, size);
        List<ProductResponse> items = found.items().stream().map(ProductResponse::from).toList();
        return new Page<>(items, found.total(), found.page(), found.size(), found.pages());
    }

    @GetMapping("/{id}")
    public ProductResponse get(@PathVariable String id) {
        return ProductResponse.from(catalog.get(id));
    }

    @PostMapping("/{id}/stock-additions")
    public ProductResponse addStock(@PathVariable String id, @RequestBody StockRequest req) {
        return ProductResponse.from(catalog.addStock(id, req.quantity()));
    }

    @PostMapping("/{id}/stock-reductions")
    public ProductResponse reduceStock(@PathVariable String id, @RequestBody StockRequest req) {
        return ProductResponse.from(catalog.reduceStock(id, req.quantity()));
    }

    @PostMapping("/{id}/archive")
    public ProductResponse archive(@PathVariable String id) {
        return ProductResponse.from(catalog.archive(id));
    }
}
