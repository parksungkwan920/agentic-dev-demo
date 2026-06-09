package kr.elice.shop.inventory.application;

import java.util.UUID;
import kr.elice.shop.catalog.application.CatalogService;
import kr.elice.shop.inventory.domain.Reservation;
import kr.elice.shop.inventory.domain.ReservationRepository;
import kr.elice.shop.shared.DomainException;
import kr.elice.shop.shared.ErrorCode;
import org.springframework.stereotype.Service;

/**
 * 재고 예약 응용 서비스입니다. 가용분 = 물리 재고 - 묶여 있는(RESERVED) 예약 합계로 계산합니다.
 * 예약은 물리 재고를 건드리지 않고, 확정 시에만 catalog 의 물리 재고를 실제로 차감합니다.
 *
 * <p>reserve 는 "가용분 확인 후 예약 생성"이 원자적으로 일어나야 oversell 을 막을 수 있으므로
 * synchronized 로 직렬화합니다. 동시 요청 100건이 와도 물리 재고를 넘겨 팔지 않습니다.</p>
 */
@Service
public class InventoryService {

    private final CatalogService catalog;
    private final ReservationRepository reservations;

    public InventoryService(CatalogService catalog, ReservationRepository reservations) {
        this.catalog = catalog;
        this.reservations = reservations;
    }

    /** 가용분 안에서 예약을 잡습니다. 가용분을 넘으면 INSUFFICIENT_STOCK 으로 거부합니다. */
    public synchronized Reservation reserve(String productId, int quantity) {
        if (quantity <= 0) {
            throw new DomainException(ErrorCode.INVALID_QUANTITY, "예약 수량은 1 이상이어야 합니다");
        }
        int available = available(productId);
        if (quantity > available) {
            throw new DomainException(ErrorCode.INSUFFICIENT_STOCK, "가용 재고가 부족합니다");
        }
        Reservation reservation =
                Reservation.open("resv_" + UUID.randomUUID().toString().substring(0, 8), productId, quantity);
        return reservations.save(reservation);
    }

    /** 예약을 확정해 물리 재고를 실제로 차감합니다. */
    public synchronized void confirm(String reservationId) {
        Reservation reservation = find(reservationId);
        catalog.reduceStock(reservation.productId(), reservation.quantity());
        reservation.confirm();
        reservations.save(reservation);
    }

    /** 예약을 해제해 가용분을 되돌립니다. */
    public synchronized void release(String reservationId) {
        Reservation reservation = find(reservationId);
        reservation.release();
        reservations.save(reservation);
    }

    /**
     * 주문 취소 보상에서 예약 하나를 되돌립니다. 아직 RESERVED 이면 풀어 가용분을 되돌리고,
     * 이미 CONFIRMED 라 물리 재고가 빠졌으면 그만큼 물리 재고를 더해 복원합니다. RELEASED 는 무시합니다.
     */
    public synchronized void cancel(String reservationId) {
        Reservation reservation = find(reservationId);
        switch (reservation.status()) {
            case RESERVED -> {
                reservation.release();
                reservations.save(reservation);
            }
            case CONFIRMED -> {
                catalog.addStock(reservation.productId(), reservation.quantity());
                reservation.restore();
                reservations.save(reservation);
            }
            case RELEASED -> {
                // 이미 되돌려졌으면 멱등하게 아무것도 하지 않습니다.
            }
        }
    }

    /** 현재 가용분(물리 재고에서 묶여 있는 예약을 뺀 값)을 돌려줍니다. */
    public synchronized int available(String productId) {
        int physical = catalog.get(productId).stockQuantity();
        int held = reservations.findByProductId(productId).stream()
                .filter(Reservation::holdsAvailability)
                .mapToInt(Reservation::quantity)
                .sum();
        return physical - held;
    }

    private Reservation find(String reservationId) {
        return reservations.findById(reservationId)
                .orElseThrow(() -> new DomainException(ErrorCode.NOT_FOUND, "예약을 찾을 수 없습니다: " + reservationId));
    }
}
