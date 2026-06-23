package kr.elice.realfield.ingestion.client;

import org.springframework.context.annotation.Profile;
import org.springframework.stereotype.Component;

import java.util.List;

/**
 * 오프라인 E2E용 스텁. stub 프로필에서만 활성화됩니다.
 * 서울 종로구(11110) 2024년 5월: 정상 4건 + 해제 1건.
 * 정상 거래금액(만원): 70,000 / 80,000 / 90,000 / 100,000
 * 중위값 = (80,000 + 90,000)/2 = 85,000만원 = 850,000,000원 (결정적)
 */
@Component
@Profile("stub")
public class StubAptTradeSource implements AptTradeSource {

    @Override
    public List<MolitAptTradeItem> fetchAptTrades(String lawdCd, String dealYmd) {
        return List.of(
            new MolitAptTradeItem("11110", "청운동", "123", "경복궁아파트", "84.97", "2024", "5", "10", " 70,000", "5",  "2003", "중개거래", null, null),
            new MolitAptTradeItem("11110", "청운동", "124", "경복궁아파트", "84.97", "2024", "5", "12", " 80,000", "10", "2003", "중개거래", null, null),
            new MolitAptTradeItem("11110", "사직동", "200", "사직파크",     "59.94", "2024", "5", "15", " 90,000", "8",  "2010", "직거래",   null, null),
            new MolitAptTradeItem("11110", "사직동", "201", "사직파크",     "59.94", "2024", "5", "18", "100,000", "12", "2010", "중개거래", null, null),
            new MolitAptTradeItem("11110", "청운동", "125", "경복궁아파트", "84.97", "2024", "5", "20", "999,999", "9",  "2003", "중개거래", "O", "24.06.01")
        );
    }
}
