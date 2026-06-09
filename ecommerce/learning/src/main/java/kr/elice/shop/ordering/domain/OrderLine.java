package kr.elice.shop.ordering.domain;

import kr.elice.shop.shared.DomainException;
import kr.elice.shop.shared.ErrorCode;
import kr.elice.shop.shared.Money;

/**
 * 주문 라인입니다. 주문 시점의 상품명과 단가를 스냅샷으로 고정해, 이후 상품 가격이 바뀌어도
 * 주문 금액은 변하지 않게 합니다.
 */
public class OrderLine {

    private final String productId;
    private final String name;
    private final Money unitPrice;
    private final int quantity;

    public OrderLine(String productId, String name, Money unitPrice, int quantity) {
        if (quantity <= 0) {
            throw new DomainException(ErrorCode.INVALID_QUANTITY, "주문 수량은 1 이상이어야 합니다");
        }
        this.productId = productId;
        this.name = name;
        this.unitPrice = unitPrice;
        this.quantity = quantity;
    }

    /** 이 라인의 소계(단가 × 수량)를 돌려줍니다. */
    public Money subtotal() {
        return unitPrice.times(quantity);
    }

    public String productId() {
        return productId;
    }

    public String name() {
        return name;
    }

    public Money unitPrice() {
        return unitPrice;
    }

    public int quantity() {
        return quantity;
    }
}
