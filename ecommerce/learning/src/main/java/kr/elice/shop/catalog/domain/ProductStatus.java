package kr.elice.shop.catalog.domain;

/** 상품 수명주기 상태입니다. ACTIVE 만 재고 변경과 판매가 가능합니다. */
public enum ProductStatus {
    ACTIVE,
    ARCHIVED
}
