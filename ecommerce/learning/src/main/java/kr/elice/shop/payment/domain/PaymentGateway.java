package kr.elice.shop.payment.domain;

import kr.elice.shop.shared.Money;

/**
 * 결제 게이트웨이 포트입니다. 외부 PG 연동을 추상화합니다. 데모 어댑터는 수단 이름에 따라
 * 결정적으로 승인·거절해, 테스트가 외부 의존 없이 재현 가능하게 합니다.
 */
public interface PaymentGateway {

    /** 결제를 시도합니다. 승인되면 true, 거절되면 false 를 돌려줍니다. */
    boolean charge(String orderId, String method, Money amount);
}
