package kr.elice.shop.inventory.web;

import kr.elice.shop.inventory.application.InventoryService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/** 재고 조회 REST 표면입니다. 가용분을 노출합니다. */
@RestController
@RequestMapping("/api/inventory")
public class InventoryController {

    private final InventoryService inventory;

    public InventoryController(InventoryService inventory) {
        this.inventory = inventory;
    }

    public record AvailabilityResponse(String productId, int available) {}

    @GetMapping("/{productId}")
    public AvailabilityResponse available(@PathVariable String productId) {
        return new AvailabilityResponse(productId, inventory.available(productId));
    }
}
