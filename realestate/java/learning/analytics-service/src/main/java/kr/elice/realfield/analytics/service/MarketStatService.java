package kr.elice.realfield.analytics.service;

import kr.elice.realfield.analytics.domain.MarketStat;
import kr.elice.realfield.analytics.domain.MarketStatCalculator;
import kr.elice.realfield.common.AptTransaction;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.List;

/**
 * 시세 통계 조회 서비스입니다. 거래원장(write model)에서 거래를 읽어와 read model로 집계합니다.
 * 운영 확장에서는 적재 이벤트를 구독해 read model을 미리 갱신하지만, 데모는 조회 시 집계로 단순화합니다.
 */
@Service
public class MarketStatService {

    private final WebClient transactionClient;
    private final MarketStatCalculator calculator;

    public MarketStatService(WebClient.Builder loadBalancedWebClientBuilder,
                             @Value("${transaction.base-url}") String transactionBaseUrl,
                             MarketStatCalculator calculator) {
        this.transactionClient = loadBalancedWebClientBuilder.baseUrl(transactionBaseUrl).build();
        this.calculator = calculator;
    }

    public MarketStat marketStat(String sggCd, int dealYear, int dealMonth) {
        List<AptTransaction> transactions = transactionClient.get()
                .uri(uri -> uri.path("/api/v1/transactions")
                        .queryParam("sggCd", sggCd)
                        .queryParam("dealYear", dealYear)
                        .queryParam("dealMonth", dealMonth)
                        .build())
                .retrieve()
                .bodyToMono(new ParameterizedTypeReference<List<AptTransaction>>() {})
                .block();

        return calculator.calculate(sggCd, dealYear, dealMonth,
                transactions == null ? List.of() : transactions);
    }
}
