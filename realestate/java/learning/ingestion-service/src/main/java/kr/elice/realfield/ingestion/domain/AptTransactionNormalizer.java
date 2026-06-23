package kr.elice.realfield.ingestion.domain;

import kr.elice.realfield.common.AptTransaction;
import kr.elice.realfield.common.DealAmountParser;
import kr.elice.realfield.ingestion.client.MolitAptTradeItem;
import org.springframework.stereotype.Component;

/**
 * MolitAptTradeItem(raw)을 표준 AptTransaction으로 정규화합니다.
 * AC-3: 거래금액 콤마 변환, cdealType=O이면 canceled=true.
 */
@Component
public class AptTransactionNormalizer {

    public AptTransaction normalize(MolitAptTradeItem raw) {
        boolean canceled = "O".equalsIgnoreCase(safeTrim(raw.cdealType()));
        return new AptTransaction(
                safeTrim(raw.sggCd()),
                safeTrim(raw.umdNm()),
                safeTrim(raw.aptNm()),
                parseDouble(raw.excluUseAr()),
                parseInt(raw.floor()),
                parseInt(raw.buildYear()),
                parseInt(raw.dealYear()),
                parseInt(raw.dealMonth()),
                parseInt(raw.dealDay()),
                DealAmountParser.toWon(raw.dealAmount()),
                canceled
        );
    }

    private static String safeTrim(String s) {
        return s == null ? "" : s.trim();
    }

    private static int parseInt(String s) {
        return (s == null || s.isBlank()) ? 0 : Integer.parseInt(s.trim());
    }

    private static double parseDouble(String s) {
        return (s == null || s.isBlank()) ? 0d : Double.parseDouble(s.trim());
    }
}
