package kr.elice.shop.shared;

/**
 * 도메인 불변식 위반을 표현하는 예외입니다. 모든 비즈니스 규칙 위반은 이 예외 한 종류로
 * 던지고, {@link ErrorCode} 로 종류를 구분합니다. web 계층은 code 의 httpStatus 로 응답을 만듭니다.
 */
public class DomainException extends RuntimeException {

    private final ErrorCode code;

    public DomainException(ErrorCode code, String message) {
        super(message);
        this.code = code;
    }

    public DomainException(ErrorCode code) {
        this(code, code.name());
    }

    /** 이 예외가 나타내는 오류 코드를 돌려줍니다. */
    public ErrorCode code() {
        return code;
    }
}
