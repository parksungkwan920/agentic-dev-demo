package kr.elice.shop.catalog.web;

import kr.elice.shop.catalog.domain.Product;

/** 상품 응답 DTO 입니다. 금액은 long 으로 평탄화해 JSON 으로 내보냅니다. */
public record ProductResponse(String id, String name, long price, int stockQuantity, String status) {

    public static ProductResponse from(Product product) {
        return new ProductResponse(
                product.id(),
                product.name(),
                product.price().amount(),
                product.stockQuantity(),
                product.status().name());
    }
}
