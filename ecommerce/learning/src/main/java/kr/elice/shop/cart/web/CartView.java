package kr.elice.shop.cart.web;

import java.util.List;

/**
 * 장바구니 조회 뷰입니다. 각 항목의 단가는 조회 시점의 카탈로그 가격 스냅샷이고, 총액은 그 합입니다.
 */
public record CartView(String cartId, List<Line> items, long totalAmount) {

    public record Line(String productId, String name, long unitPrice, int qty, long subtotal) {}
}
