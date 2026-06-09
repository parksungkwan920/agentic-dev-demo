package kr.elice.shop.shared;

/**
 * 도메인 오류 코드와 HTTP 상태 매핑입니다. 도메인 계층은 프레임워크에 의존하지 않으므로
 * 상태 코드를 int 로만 들고 있고, 실제 HTTP 변환은 web 계층의 예외 핸들러가 담당합니다.
 */
public enum ErrorCode {
    INVALID_PRICE(400),
    INVALID_AMOUNT(400),
    INVALID_QUANTITY(400),
    INSUFFICIENT_STOCK(409),
    PRODUCT_ARCHIVED(409),
    INVALID_STATE_TRANSITION(409),
    PAYMENT_REQUIRED(409),
    REFUND_NOT_ALLOWED(409),
    PAYMENT_DECLINED(402),
    NOT_FOUND(404);

    private final int httpStatus;

    ErrorCode(int httpStatus) {
        this.httpStatus = httpStatus;
    }

    /** 이 오류 코드가 대응하는 HTTP 상태 코드를 돌려줍니다. */
    public int httpStatus() {
        return httpStatus;
    }
}
