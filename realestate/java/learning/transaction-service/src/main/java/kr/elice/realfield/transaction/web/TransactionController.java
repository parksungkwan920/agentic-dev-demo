package kr.elice.realfield.transaction.web;

import kr.elice.realfield.common.AptTransaction;
import kr.elice.realfield.transaction.service.TransactionCommandService;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/** 거래원장 API입니다. 게이트웨이가 {@code /api/v1/transactions/**} 를 이 서비스로 라우팅합니다. */
@RestController
@RequestMapping("/api/v1/transactions")
public class TransactionController {

    private final TransactionCommandService commandService;

    public TransactionController(TransactionCommandService commandService) {
        this.commandService = commandService;
    }

    /** 수집 서비스가 정규화 거래를 묶어 보냅니다. 새로 적재된 건수를 돌려줍니다(멱등). */
    @PostMapping("/bulk")
    public int upsertBulk(@RequestBody List<AptTransaction> transactions) {
        return commandService.upsertAll(transactions);
    }

    /** 예) GET /api/v1/transactions?sggCd=11110&dealYear=2024&dealMonth=5 */
    @GetMapping
    public List<AptTransaction> query(@RequestParam String sggCd,
                                      @RequestParam int dealYear,
                                      @RequestParam int dealMonth) {
        return commandService.query(sggCd, dealYear, dealMonth);
    }
}
