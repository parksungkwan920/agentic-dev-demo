package kr.elice.shop.inventory.domain;

import kr.elice.shop.shared.DomainException;
import kr.elice.shop.shared.ErrorCode;

/**
 * 재고 예약 애그리거트입니다. 예약은 물리 재고를 줄이지 않고 가용분만 묶어 둡니다.
 * 확정되면 물리 재고로 빠지고, 해제되면 가용분으로 되돌아갑니다. 상태 전환만 이 안에서 통제합니다.
 */
public class Reservation {

    private final String id;
    private final String productId;
    private final int quantity;
    private ReservationStatus status;

    private Reservation(String id, String productId, int quantity, ReservationStatus status) {
        this.id = id;
        this.productId = productId;
        this.quantity = quantity;
        this.status = status;
    }

    /** RESERVED 상태의 새 예약을 엽니다. */
    public static Reservation open(String id, String productId, int quantity) {
        if (quantity <= 0) {
            throw new DomainException(ErrorCode.INVALID_QUANTITY, "예약 수량은 1 이상이어야 합니다");
        }
        return new Reservation(id, productId, quantity, ReservationStatus.RESERVED);
    }

    /** 예약을 확정합니다. RESERVED 가 아니면 거부합니다. */
    public void confirm() {
        if (status != ReservationStatus.RESERVED) {
            throw new DomainException(ErrorCode.INVALID_STATE_TRANSITION, "RESERVED 예약만 확정할 수 있습니다");
        }
        this.status = ReservationStatus.CONFIRMED;
    }

    /** 예약을 해제합니다. 이미 확정된 예약은 해제할 수 없습니다. */
    public void release() {
        if (status == ReservationStatus.CONFIRMED) {
            throw new DomainException(ErrorCode.INVALID_STATE_TRANSITION, "확정된 예약은 해제할 수 없습니다");
        }
        this.status = ReservationStatus.RELEASED;
    }

    /**
     * 확정된 예약을 되돌립니다. 결제 후 취소 보상에서 물리 재고를 되돌릴 때 함께 호출합니다.
     * 물리 재고 복원은 서비스가 책임지고, 이 메서드는 예약 상태만 RELEASED 로 바꿉니다.
     */
    public void restore() {
        if (status != ReservationStatus.CONFIRMED) {
            throw new DomainException(ErrorCode.INVALID_STATE_TRANSITION, "확정된 예약만 되돌릴 수 있습니다");
        }
        this.status = ReservationStatus.RELEASED;
    }

    /** 이 예약이 아직 가용분을 묶고 있는지(RESERVED) 알려줍니다. */
    public boolean holdsAvailability() {
        return status == ReservationStatus.RESERVED;
    }

    public String id() {
        return id;
    }

    public String productId() {
        return productId;
    }

    public int quantity() {
        return quantity;
    }

    public ReservationStatus status() {
        return status;
    }
}
