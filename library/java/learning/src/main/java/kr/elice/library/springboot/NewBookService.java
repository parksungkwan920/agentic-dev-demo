package kr.elice.library.springboot;

import java.util.List;
import kr.elice.library.api.BookService;
import kr.elice.library.domain.Book;
import kr.elice.library.domain.LibraryException;
import kr.elice.library.store.BookStore;
import org.springframework.stereotype.Service;

/**
 * Spring Boot 스타일 도서 모듈 구현체입니다.
 * LegacyBookService 를 대체하는 신규 구현이며, 공유 BookStore 를 통해 동일 데이터에 접근합니다.
 */
@Service
public class NewBookService implements BookService {

    private final BookStore store;

    public NewBookService(BookStore store) {
        this.store = store;
    }

    @Override
    public Book register(String title) {
        // 새 ID 생성 후 도서 저장
        return store.save(new Book(store.nextId(), title));
    }

    @Override
    public Book get(String id) {
        // 도서 조회 실패 시 NOT_FOUND 예외 발생
        return store.find(id).orElseThrow(() ->
                new LibraryException(LibraryException.Code.NOT_FOUND, "도서를 찾을 수 없습니다: " + id));
    }

    @Override
    public List<Book> list() {
        return store.all();
    }
}
