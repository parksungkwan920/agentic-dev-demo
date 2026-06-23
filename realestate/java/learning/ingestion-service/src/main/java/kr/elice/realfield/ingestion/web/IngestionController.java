package kr.elice.realfield.ingestion.web;

import kr.elice.realfield.ingestion.service.IngestionService;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/v1/ingest")
public class IngestionController {

    private final IngestionService ingestionService;

    public IngestionController(IngestionService ingestionService) {
        this.ingestionService = ingestionService;
    }

    @PostMapping("/apt-trade")
    public Map<String, Object> ingestAptTrade(@RequestParam String lawdCd,
                                              @RequestParam String dealYmd) {
        int upserted = ingestionService.ingest(lawdCd, dealYmd);
        return Map.of("lawdCd", lawdCd, "dealYmd", dealYmd, "upserted", upserted);
    }
}
