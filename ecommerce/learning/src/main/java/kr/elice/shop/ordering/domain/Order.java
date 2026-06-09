package kr.elice.shop.ordering.domain;

import java.util.List;
import kr.elice.shop.shared.DomainException;
import kr.elice.shop.shared.ErrorCode;
import kr.elice.shop.shared.Money;

/**
 * 주문 애그리거트이자 상태머신입니다. 생성 시 총액이 0원 이하이면 거부하고, 이후 상태 전환
 * (결제·이행·취소)의 정당성을 모두 이 안에서 통제합니다. 잡아 둔 예약 id 도 함께 들고 있어
 * 취소 보상 시 어떤 예약을 풀어야 하는지 알 수 있습니다.
 */
public class Order {

    private final String id;
    private final List<OrderLine> lines;
    private final List<String> reservationIds;
    private final Money totalAmount;
    private OrderStatus status;
    private String paymentId;

    private Order(String id, List<OrderLine> lines, List<String> reservationIds, Money totalAmount) {
        this.id = id;
        this.lines = List.copyOf(lines);
        this.reservationIds = List.copyOf(reservationIds);
        this.totalAmount = totalAmount;
        this.status = OrderStatus.CREATED;
    }

    /** CREATED 상태의 새 주문을 만듭니다. 총액이 0원 이하이면 INVALID_AMOUNT 로 거부합니다. */
    public static Order create(String id, List<OrderLine> lines, List<String> reservationIds) {
        Money total = lines.stream().map(OrderLine::subtotal).reduce(Money.zero(), Money::plus);
        if (total.isZeroOrLess()) {
            throw new DomainException(ErrorCode.INVALID_AMOUNT, "주문 총액은 0원보다 커야 합니다");
        }
        return new Order(id, lines, reservationIds, total);
    }

    /** 결제 완료로 주문을 PAID 로 전환합니다. CREATED 가 아니면 거부합니다. */
    public void markPaid(String paymentId) {
        if (status != OrderStatus.CREATED) {
            throw new DomainException(ErrorCode.INVALID_STATE_TRANSITION, "CREATED 주문만 결제할 수 있습니다");
        }
        this.paymentId = paymentId;
        this.status = OrderStatus.PAID;
    }

    /** 주문을 이행합니다. 결제 전 주문은 PAYMENT_REQUIRED 로 거부합니다. */
    public void fulfill() {
        if (status != OrderStatus.PAID) {
            throw new DomainException(ErrorCode.PAYMENT_REQUIRED, "결제된 주문만 이행할 수 있습니다");
        }
        this.status = OrderStatus.FULFILLED;
    }

    /**
     * 주문을 취소합니다. 결제된 주문이었다면 환불이 필요하다는 신호로 true 를 돌려줍니다.
     * 이미 이행됐거나 취소된 주문은 INVALID_STATE_TRANSITION 으로 거부합니다.
     */
    public boolean cancel() {
        if (status == OrderStatus.CREATED) {
            this.status = OrderStatus.CANCELLED;
            return false;
        }
        if (status == OrderStatus.PAID) {
            this.status = OrderStatus.CANCELLED;
            return true;
        }
        throw new DomainException(ErrorCode.INVALID_STATE_TRANSITION, "이행되었거나 취소된 주문은 취소할 수 없습니다");
    }

    public String id() {
        return id;
    }

    public List<OrderLine> lines() {
        return lines;
    }

    public List<String> reservationIds() {
        return reservationIds;
    }

    public Money totalAmount() {
        return totalAmount;
    }

    public OrderStatus status() {
        return status;
    }

    public String paymentId() {
        return paymentId;
    }
}
