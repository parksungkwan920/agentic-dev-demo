package kr.elice.shop.ordering.domain;

/**
 * 주문 상태입니다. 정방향은 CREATED → PAID → FULFILLED 로만 흐르고, CREATED·PAID 에서만
 * CANCELLED 로 갈 수 있습니다. FULFILLED 와 CANCELLED 는 종착 상태입니다.
 */
public enum OrderStatus {
    CREATED,
    PAID,
    FULFILLED,
    CANCELLED
}
