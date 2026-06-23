package kr.elice.realfield.ingestion.service;

import kr.elice.realfield.common.AptTransaction;
import kr.elice.realfield.ingestion.client.AptTradeSource;
import kr.elice.realfield.ingestion.domain.AptTransactionNormalizer;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.List;

@Service
public class IngestionService {

    private final AptTradeSource source;
    private final AptTransactionNormalizer normalizer;
    private final WebClient transactionClient;

    public IngestionService(AptTradeSource source,
                            AptTransactionNormalizer normalizer,
                            WebClient.Builder builder,
                            @Value("${transaction.base-url}") String transactionBaseUrl) {
        this.source = source;
        this.normalizer = normalizer;
        this.transactionClient = builder.baseUrl(transactionBaseUrl).build();
    }

    public int ingest(String lawdCd, String dealYmd) {
        List<AptTransaction> normalized = source.fetchAptTrades(lawdCd, dealYmd).stream()
                .map(normalizer::normalize)
                .toList();

        if (normalized.isEmpty()) return 0;

        // AC-4: transaction-service가 자연키로 멱등 upsert 합니다.
        Integer upserted = transactionClient.post()
                .uri("/api/v1/transactions/bulk")
                .bodyValue(normalized)
                .retrieve()
                .bodyToMono(Integer.class)
                .block();

        return upserted == null ? 0 : upserted;
    }
}
