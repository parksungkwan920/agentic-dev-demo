package kr.elice.realfield.ingestion.client;

import java.util.List;

public interface AptTradeSource {
    List<MolitAptTradeItem> fetchAptTrades(String lawdCd, String dealYmd);
}
