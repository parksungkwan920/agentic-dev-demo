package kr.elice.shop.inventory.domain;

/**
 * 예약 상태입니다. RESERVED 만 가용분을 묶어 둡니다. CONFIRMED 는 물리 재고로 확정된 상태이고,
 * RELEASED 는 풀려 가용분으로 되돌아간 상태입니다.
 */
public enum ReservationStatus {
    RESERVED,
    CONFIRMED,
    RELEASED
}
