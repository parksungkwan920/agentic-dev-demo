package kr.elice.shop.payment.infrastructure;

import kr.elice.shop.payment.domain.PaymentGateway;
import kr.elice.shop.shared.Money;
import org.springframework.stereotype.Component;

/**
 * 데모 결제 게이트웨이 어댑터입니다. 외부 PG 없이 결정적으로 동작해 테스트가 재현 가능합니다.
 * 수단 이름이 "declined" 이면 거절하고, 그 외에는 승인합니다.
 */
@Component
public class DemoPaymentGateway implements PaymentGateway {

    @Override
    public boolean charge(String orderId, String method, Money amount) {
        return !"declined".equalsIgnoreCase(method);
    }
}
