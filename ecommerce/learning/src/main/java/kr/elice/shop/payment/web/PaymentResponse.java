package kr.elice.shop.payment.web;

import kr.elice.shop.payment.domain.Payment;

/** 결제 응답 DTO 입니다. */
public record PaymentResponse(String id, String orderId, String method, long amount, String status) {

    public static PaymentResponse from(Payment payment) {
        return new PaymentResponse(
                payment.id(),
                payment.orderId(),
                payment.method(),
                payment.amount().amount(),
                payment.status().name());
    }
}
