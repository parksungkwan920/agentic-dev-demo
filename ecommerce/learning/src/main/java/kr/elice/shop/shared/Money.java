package kr.elice.shop.shared;

import java.util.Objects;

/**
 * 원화 금액 값 객체입니다. 음수 금액을 허용하지 않아 잘못된 가격이 시스템에 들어오는 것을
 * 입구에서 막습니다. 0원은 생성 자체는 허용하되, 가격·총액 불변식은 각 애그리거트가 검사합니다.
 */
public final class Money {

    private final long amount;

    private Money(long amount) {
        if (amount < 0) {
            throw new DomainException(ErrorCode.INVALID_AMOUNT, "금액은 음수일 수 없습니다: " + amount);
        }
        this.amount = amount;
    }

    /** 주어진 원화 금액으로 Money 를 만듭니다. */
    public static Money won(long amount) {
        return new Money(amount);
    }

    /** 0원 Money 를 돌려줍니다. 합산의 시작값으로 씁니다. */
    public static Money zero() {
        return new Money(0);
    }

    /** 원화 금액을 long 으로 돌려줍니다. */
    public long amount() {
        return amount;
    }

    /** 두 금액을 더한 새 Money 를 돌려줍니다. */
    public Money plus(Money other) {
        return new Money(this.amount + other.amount);
    }

    /** 금액에 수량을 곱한 새 Money 를 돌려줍니다. 수량은 음수일 수 없습니다. */
    public Money times(int factor) {
        if (factor < 0) {
            throw new DomainException(ErrorCode.INVALID_QUANTITY, "수량은 음수일 수 없습니다: " + factor);
        }
        return new Money(this.amount * factor);
    }

    /** 금액이 0원보다 큰지 알려줍니다. */
    public boolean isPositive() {
        return amount > 0;
    }

    /** 금액이 0원 이하인지 알려줍니다. 가격·총액 거부 판정에 씁니다. */
    public boolean isZeroOrLess() {
        return amount <= 0;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) {
            return true;
        }
        if (!(o instanceof Money other)) {
            return false;
        }
        return amount == other.amount;
    }

    @Override
    public int hashCode() {
        return Objects.hash(amount);
    }

    @Override
    public String toString() {
        return amount + "원";
    }
}
