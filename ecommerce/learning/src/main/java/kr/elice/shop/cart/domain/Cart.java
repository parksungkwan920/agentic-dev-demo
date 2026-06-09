package kr.elice.shop.cart.domain;

import java.util.LinkedHashMap;
import java.util.Map;
import kr.elice.shop.shared.DomainException;
import kr.elice.shop.shared.ErrorCode;

/**
 * 장바구니 애그리거트입니다. 같은 상품을 다시 담으면 수량을 합치고, 수량을 0으로 바꾸면 항목을
 * 제거합니다. 상품 단가·아카이브 여부 같은 카탈로그 규칙은 모르고, 오직 상품별 수량만 관리합니다.
 */
public class Cart {

    private final String id;
    private final Map<String, Integer> items = new LinkedHashMap<>();

    public Cart(String id) {
        this.id = id;
    }

    /** 상품을 담습니다. 이미 있는 상품이면 수량을 합칩니다. */
    public void addItem(String productId, int quantity) {
        if (quantity <= 0) {
            throw new DomainException(ErrorCode.INVALID_QUANTITY, "담는 수량은 1 이상이어야 합니다");
        }
        items.merge(productId, quantity, Integer::sum);
    }

    /** 수량을 바꿉니다. 0 이하로 바꾸면 항목을 제거합니다. */
    public void updateQuantity(String productId, int quantity) {
        if (quantity <= 0) {
            items.remove(productId);
            return;
        }
        items.put(productId, quantity);
    }

    /** 항목을 제거합니다. */
    public void removeItem(String productId) {
        items.remove(productId);
    }

    /** 장바구니를 비웁니다. */
    public void clear() {
        items.clear();
    }

    public String id() {
        return id;
    }

    /** 상품별 수량 매핑의 읽기 전용 사본을 돌려줍니다. */
    public Map<String, Integer> items() {
        return Map.copyOf(items);
    }
}
