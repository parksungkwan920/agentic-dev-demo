package kr.elice.shop.cart.web;

import kr.elice.shop.cart.application.CartService;
import kr.elice.shop.cart.domain.Cart;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/** 장바구니 REST 표면입니다. 생성·조회·담기·수량변경·삭제·비우기를 노출합니다. */
@RestController
@RequestMapping("/api/carts")
public class CartController {

    private final CartService carts;

    public CartController(CartService carts) {
        this.carts = carts;
    }

    public record CartCreatedResponse(String cartId) {}

    public record AddItemRequest(String productId, int qty) {}

    public record UpdateQtyRequest(int qty) {}

    @PostMapping
    public ResponseEntity<CartCreatedResponse> create() {
        Cart cart = carts.create();
        return ResponseEntity.status(HttpStatus.CREATED).body(new CartCreatedResponse(cart.id()));
    }

    @GetMapping("/{id}")
    public CartView get(@PathVariable String id) {
        return carts.view(id);
    }

    @PostMapping("/{id}/items")
    public CartView addItem(@PathVariable String id, @RequestBody AddItemRequest req) {
        return carts.addItem(id, req.productId(), req.qty());
    }

    @PatchMapping("/{id}/items/{productId}")
    public CartView updateQuantity(
            @PathVariable String id, @PathVariable String productId, @RequestBody UpdateQtyRequest req) {
        return carts.updateQuantity(id, productId, req.qty());
    }

    @DeleteMapping("/{id}/items/{productId}")
    public CartView removeItem(@PathVariable String id, @PathVariable String productId) {
        return carts.removeItem(id, productId);
    }

    @PostMapping("/{id}/clear")
    public CartView clear(@PathVariable String id) {
        return carts.clear(id);
    }
}
