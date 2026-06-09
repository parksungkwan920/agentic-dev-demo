package kr.elice.shop.payment.domain;

import kr.elice.shop.shared.DomainException;
import kr.elice.shop.shared.ErrorCode;
import kr.elice.shop.shared.Money;

/**
 * 결제 애그리거트입니다. 승인된 결제는 CAPTURED 로 시작하고, 환불은 CAPTURED 상태에서만
 * 가능합니다. 캡처되지 않은(이미 환불된) 결제를 다시 환불하려 하면 REFUND_NOT_ALLOWED 로 거부합니다.
 */
public class Payment {

    private final String id;
    private final String orderId;
    private final String method;
    private final Money amount;
    private PaymentStatus status;

    private Payment(String id, String orderId, String method, Money amount, PaymentStatus status) {
        this.id = id;
        this.orderId = orderId;
        this.method = method;
        this.amount = amount;
        this.status = status;
    }

    /** 승인·캡처된 결제를 만듭니다. */
    public static Payment capture(String id, String orderId, String method, Money amount) {
        return new Payment(id, orderId, method, amount, PaymentStatus.CAPTURED);
    }

    /** 결제를 환불합니다. 캡처된 결제가 아니면 REFUND_NOT_ALLOWED 로 거부합니다. */
    public void refund() {
        if (status != PaymentStatus.CAPTURED) {
            throw new DomainException(ErrorCode.REFUND_NOT_ALLOWED, "캡처된 결제만 환불할 수 있습니다");
        }
        this.status = PaymentStatus.REFUNDED;
    }

    public String id() {
        return id;
    }

    public String orderId() {
        return orderId;
    }

    public String method() {
        return method;
    }

    public Money amount() {
        return amount;
    }

    public PaymentStatus status() {
        return status;
    }
}
