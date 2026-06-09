package kr.elice.shop.catalog.domain;

import kr.elice.shop.shared.DomainException;
import kr.elice.shop.shared.ErrorCode;
import kr.elice.shop.shared.Money;

/**
 * 상품 애그리거트입니다. 가격·재고·상태에 관한 모든 불변식을 이 안에 모읍니다.
 * 가격은 0원 이하일 수 없고, 재고는 음수가 될 수 없으며, ARCHIVED 상품은 재고를 바꿀 수 없습니다.
 */
public class Product {

    private final String id;
    private String name;
    private Money price;
    private int stockQuantity;
    private ProductStatus status;

    private Product(String id, String name, Money price, int stockQuantity, ProductStatus status) {
        this.id = id;
        this.name = name;
        this.price = price;
        this.stockQuantity = stockQuantity;
        this.status = status;
    }

    /** ACTIVE 상태의 새 상품을 만듭니다. 가격이 0원 이하이면 생성을 거부합니다. */
    public static Product create(String id, String name, Money price, int initialStock) {
        if (price == null || price.isZeroOrLess()) {
            throw new DomainException(ErrorCode.INVALID_PRICE, "가격은 0원보다 커야 합니다");
        }
        if (initialStock < 0) {
            throw new DomainException(ErrorCode.INVALID_QUANTITY, "초기 재고는 음수일 수 없습니다");
        }
        return new Product(id, name, price, initialStock, ProductStatus.ACTIVE);
    }

    /** 재고를 더합니다. ARCHIVED 상품은 거부합니다. */
    public void addStock(int quantity) {
        ensureActive();
        requirePositive(quantity);
        this.stockQuantity += quantity;
    }

    /** 재고를 뺍니다. 보유 재고를 넘으면 INSUFFICIENT_STOCK 으로 거부합니다. */
    public void reduceStock(int quantity) {
        ensureActive();
        requirePositive(quantity);
        if (quantity > stockQuantity) {
            throw new DomainException(ErrorCode.INSUFFICIENT_STOCK, "재고가 부족합니다");
        }
        this.stockQuantity -= quantity;
    }

    /** 상품을 아카이브합니다. 이후 모든 재고 변경이 거부됩니다. */
    public void archive() {
        this.status = ProductStatus.ARCHIVED;
    }

    private void ensureActive() {
        if (status == ProductStatus.ARCHIVED) {
            throw new DomainException(ErrorCode.PRODUCT_ARCHIVED, "아카이브된 상품은 재고를 바꿀 수 없습니다");
        }
    }

    private void requirePositive(int quantity) {
        if (quantity <= 0) {
            throw new DomainException(ErrorCode.INVALID_QUANTITY, "수량은 1 이상이어야 합니다");
        }
    }

    public String id() {
        return id;
    }

    public String name() {
        return name;
    }

    public Money price() {
        return price;
    }

    public int stockQuantity() {
        return stockQuantity;
    }

    public ProductStatus status() {
        return status;
    }

    /** 상품이 아카이브 상태인지 알려줍니다. 장바구니 담기 가드가 이 값을 봅니다. */
    public boolean isArchived() {
        return status == ProductStatus.ARCHIVED;
    }
}
