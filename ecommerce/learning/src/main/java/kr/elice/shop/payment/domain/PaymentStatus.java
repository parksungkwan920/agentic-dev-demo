package kr.elice.shop.payment.domain;

/**
 * 결제 상태입니다. 데모 게이트웨이는 승인 시 곧바로 캡처까지 끝내므로 CAPTURED 로 시작합니다.
 * 환불되면 REFUNDED 가 됩니다. 거절은 결제를 만들지 않고 예외로 처리합니다.
 */
public enum PaymentStatus {
    CAPTURED,
    REFUNDED
}
