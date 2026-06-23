package kr.elice.realfield.analytics.web;

import kr.elice.realfield.analytics.domain.MarketStat;
import kr.elice.realfield.analytics.service.MarketStatService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/** 시세 통계 조회 API입니다. 게이트웨이가 {@code /api/v1/market-stats/**} 를 라우팅합니다. */
@RestController
@RequestMapping("/api/v1/market-stats")
public class AnalyticsController {

    private final MarketStatService marketStatService;

    public AnalyticsController(MarketStatService marketStatService) {
        this.marketStatService = marketStatService;
    }

    /** 예) GET /api/v1/market-stats?sggCd=11110&dealYear=2024&dealMonth=5 */
    @GetMapping
    public MarketStat marketStat(@RequestParam String sggCd,
                                 @RequestParam int dealYear,
                                 @RequestParam int dealMonth) {
        return marketStatService.marketStat(sggCd, dealYear, dealMonth);
    }
}
