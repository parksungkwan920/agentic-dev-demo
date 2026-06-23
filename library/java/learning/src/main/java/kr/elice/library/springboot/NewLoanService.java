package kr.elice.library.springboot;

import kr.elice.library.api.LoanService;
import kr.elice.library.domain.LibraryException;
import kr.elice.library.domain.Loan;
import kr.elice.library.platform.CatalogRouter;
import kr.elice.library.store.LoanStore;
import org.springframework.stereotype.Service;

/**
 * 대출 모듈의 신규 구현입니다.
 * LegacyLoanService 와 동일한 비즈니스 로직을 수행하되,
 * 도서·회원 접근은 반드시 CatalogRouter 를 통해 위임합니다.
 */
@Service
public class NewLoanService implements LoanService {

    private static final int LIMIT = 5;

    private final CatalogRouter catalog;
    private final LoanStore store;

    public NewLoanService(CatalogRouter catalog, LoanStore store) {
        this.catalog = catalog;
        this.store = store;
    }

    @Override
    public Loan borrow(String memberId, String bookId, int daysUntilDue) {
        // 회원 존재 검증
        catalog.members().get(memberId);
        // 도서 존재 검증
        catalog.books().get(bookId);
        // AC-1: 대출 한도 초과 검사
        if (activeCount(memberId) >= LIMIT)
            throw new LibraryException(LibraryException.Code.LOAN_LIMIT_EXCEEDED, "대출 한도 5권을 초과했습니다.");
        // AC-2: 연체 중인 대출 존재 검사
        if (hasOverdue(memberId))
            throw new LibraryException(LibraryException.Code.OVERDUE_EXISTS, "연체 중인 대출이 있어 새로 빌릴 수 없습니다.");
        return store.save(new Loan(store.nextId(), memberId, bookId, daysUntilDue));
    }

    @Override
    public void giveBack(String loanId) {
        Loan loan = store.find(loanId).orElseThrow(() ->
            new LibraryException(LibraryException.Code.NOT_FOUND, "대출을 찾을 수 없습니다: " + loanId));
        loan.markReturned();
    }

    @Override
    public int activeCount(String memberId) {
        return store.activeByMember(memberId).size();
    }

    @Override
    public boolean hasOverdue(String memberId) {
        return store.activeByMember(memberId).stream().anyMatch(Loan::isOverdue);
    }
}
