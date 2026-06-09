package kr.elice.shop.cart.application;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import kr.elice.shop.cart.domain.Cart;
import kr.elice.shop.cart.domain.CartRepository;
import kr.elice.shop.catalog.application.CatalogService;
import kr.elice.shop.catalog.domain.Product;
import kr.elice.shop.cart.web.CartView;
import kr.elice.shop.shared.DomainException;
import kr.elice.shop.shared.ErrorCode;
import org.springframework.stereotype.Service;

/**
 * 장바구니 응용 서비스입니다. 담기·수량변경·삭제·비우기를 조율하고, ARCHIVED 상품 담기를 막습니다.
 * 가격은 들고 있지 않고, 조회 시 카탈로그에서 현재 단가를 읽어 스냅샷 뷰를 만듭니다.
 */
@Service
public class CartService {

    private final CartRepository carts;
    private final CatalogService catalog;

    public CartService(CartRepository carts, CatalogService catalog) {
        this.carts = carts;
        this.catalog = catalog;
    }

    /** 빈 장바구니를 만듭니다. */
    public Cart create() {
        Cart cart = new Cart("cart_" + UUID.randomUUID().toString().substring(0, 8));
        return carts.save(cart);
    }

    /** 상품을 담습니다. ARCHIVED 상품이면 PRODUCT_ARCHIVED 로 거부합니다. */
    public CartView addItem(String cartId, String productId, int qty) {
        Product product = catalog.get(productId);
        if (product.isArchived()) {
            throw new DomainException(ErrorCode.PRODUCT_ARCHIVED, "아카이브된 상품은 담을 수 없습니다");
        }
        Cart cart = get(cartId);
        cart.addItem(productId, qty);
        carts.save(cart);
        return view(cartId);
    }

    /** 항목 수량을 바꿉니다. 0 이하면 항목을 제거합니다. */
    public CartView updateQuantity(String cartId, String productId, int qty) {
        Cart cart = get(cartId);
        cart.updateQuantity(productId, qty);
        carts.save(cart);
        return view(cartId);
    }

    /** 항목을 제거합니다. */
    public CartView removeItem(String cartId, String productId) {
        Cart cart = get(cartId);
        cart.removeItem(productId);
        carts.save(cart);
        return view(cartId);
    }

    /** 장바구니를 비웁니다. */
    public CartView clear(String cartId) {
        Cart cart = get(cartId);
        cart.clear();
        carts.save(cart);
        return view(cartId);
    }

    /** 현재 카탈로그 단가로 가격 스냅샷 뷰를 만듭니다. */
    public CartView view(String cartId) {
        Cart cart = get(cartId);
        List<CartView.Line> lines = new ArrayList<>();
        long total = 0;
        for (Map.Entry<String, Integer> entry : cart.items().entrySet()) {
            Product product = catalog.get(entry.getKey());
            int qty = entry.getValue();
            long unitPrice = product.price().amount();
            long subtotal = unitPrice * qty;
            total += subtotal;
            lines.add(new CartView.Line(product.id(), product.name(), unitPrice, qty, subtotal));
        }
        return new CartView(cart.id(), lines, total);
    }

    /** id 로 장바구니를 찾습니다. 없으면 NOT_FOUND 로 거부합니다. */
    public Cart get(String cartId) {
        return carts.findById(cartId)
                .orElseThrow(() -> new DomainException(ErrorCode.NOT_FOUND, "장바구니를 찾을 수 없습니다: " + cartId));
    }
}
