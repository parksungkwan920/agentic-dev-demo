package kr.elice.library.acceptance;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import kr.elice.library.platform.LibraryApplication;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.ApplicationContext;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.test.annotation.DirtiesContext;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.context.junit.jupiter.SpringExtension;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.context.WebApplicationContext;

/**
 * 3단계 전환 완료 게이트 테스트입니다. {@code migration.properties} 를 all-new 로 강제한 뒤
 * 신규 구현 빈이 모두 등록돼 있고 수용기준(AC-1·AC-2)을 통과하는지 검증합니다.
 *
 * <p>이 테스트는 세 단계가 모두 끝나기 전까지 RED 입니다.
 * {@code NewBookService}·{@code NewMemberService}·{@code NewLoanService} 중 하나라도
 * 없으면 {@code allNewBeansRegistered} 가 실패하고, 크로스모듈 호출 테스트는
 * 라우터 예외로 실패합니다. 세 클래스가 모두 구현돼야 비로소 GREEN 이 됩니다.</p>
 *
 * <p>{@link LibraryAcceptanceTest} 는 모드에 무관한 행위 채점기입니다.
 * 이 클래스는 "신규 구현만 쓸 때도 규칙이 지켜지는가"를 별도로 보장합니다.</p>
 */
@ExtendWith(SpringExtension.class)
@SpringBootTest(classes = LibraryApplication.class)
@TestPropertySource(properties = {
    "module.books=new",
    "module.members=new",
    "module.loans=new"
})
@DirtiesContext(classMode = DirtiesContext.ClassMode.AFTER_EACH_TEST_METHOD)
class AllNewModeTest {

    @Autowired
    private WebApplicationContext wac;

    @Autowired
    private ApplicationContext ctx;

    private MockMvc mvc;
    private final ObjectMapper om = new ObjectMapper();

    @BeforeEach
    void setUp() {
        this.mvc = MockMvcBuilders.webAppContextSetup(wac).build();
    }

    // ── 헬퍼 ────────────────────────────────────────────────────────────

    private JsonNode postJson(String url, String body, HttpStatus expect) throws Exception {
        MvcResult res = mvc.perform(
                post(url).contentType(MediaType.APPLICATION_JSON).content(body))
                .andExpect(status().is(expect.value())).andReturn();
        String content = res.getResponse().getContentAsString();
        return content.isEmpty() ? om.createObjectNode() : om.readTree(content);
    }

    private String newMember(String name) throws Exception {
        return postJson("/members", "{\"name\":\"%s\"}".formatted(name), HttpStatus.CREATED)
                .get("id").asText();
    }

    private String newBook(String title) throws Exception {
        return postJson("/books", "{\"title\":\"%s\"}".formatted(title), HttpStatus.CREATED)
                .get("id").asText();
    }

    private void borrow(String memberId, String bookId, int daysUntilDue, HttpStatus expect)
            throws Exception {
        postJson("/loans",
                "{\"memberId\":\"%s\",\"bookId\":\"%s\",\"daysUntilDue\":%d}"
                        .formatted(memberId, bookId, daysUntilDue),
                expect);
    }

    // ── 테스트 ────────────────────────────────────────────────────────────

    @Test
    @DisplayName("완료 게이트: NewBookService·NewMemberService·NewLoanService 빈이 모두 등록되어 있다")
    void allNewBeansRegistered() {
        // 세 빈 중 하나라도 없으면 실패한다. 이 테스트가 빨간 불이면 아직 구현이 남아 있다.
        assertThat(ctx.containsBean("newBookService"))
                .as("springboot/NewBookService 가 @Service 로 등록되어 있어야 합니다").isTrue();
        assertThat(ctx.containsBean("newMemberService"))
                .as("springboot/NewMemberService 가 @Service 로 등록되어 있어야 합니다").isTrue();
        assertThat(ctx.containsBean("newLoanService"))
                .as("springboot/NewLoanService 가 @Service 로 등록되어 있어야 합니다").isTrue();
    }

    @Test
    @DisplayName("all-new 정상 흐름: NewLoanService 가 CatalogRouter 를 통해 NewBook·MemberService 와 협력한다")
    void newLoanUsesCatalogRouter() throws Exception {
        // NewLoanService → CatalogRouter → NewBookService·NewMemberService 크로스모듈 경로
        String memberId = newMember("allnew-정상회원");
        String bookId   = newBook("allnew-클린코드");
        JsonNode loan = postJson("/loans",
                "{\"memberId\":\"%s\",\"bookId\":\"%s\"}".formatted(memberId, bookId),
                HttpStatus.CREATED);
        assertThat(loan.get("memberId").asText()).isEqualTo(memberId);
        assertThat(loan.get("bookId").asText()).isEqualTo(bookId);
        // 반납도 신규 구현에서 동작해야 한다
        postJson("/loans/" + loan.get("id").asText() + "/return", "", HttpStatus.OK);
    }

    @Test
    @DisplayName("all-new AC-1: 신규 구현에서도 대출 한도 5권이 지켜진다")
    void ac1_loanLimitEnforcedByNewImpl() throws Exception {
        String memberId = newMember("allnew-한도회원");
        for (int i = 1; i <= 5; i++) {
            borrow(memberId, newBook("allnew-책" + i), 14, HttpStatus.CREATED);
        }
        JsonNode fail = postJson("/loans",
                "{\"memberId\":\"%s\",\"bookId\":\"%s\"}".formatted(memberId, newBook("allnew-책6")),
                HttpStatus.CONFLICT);
        assertThat(fail.get("code").asText()).isEqualTo("LOAN_LIMIT_EXCEEDED");
    }

    @Test
    @DisplayName("all-new AC-2: 신규 구현에서도 연체 중이면 새 대출이 거부된다")
    void ac2_overdueBlocksEnforcedByNewImpl() throws Exception {
        String memberId = newMember("allnew-연체회원");
        borrow(memberId, newBook("allnew-연체된책"), -3, HttpStatus.CREATED);
        JsonNode fail = postJson("/loans",
                "{\"memberId\":\"%s\",\"bookId\":\"%s\"}".formatted(memberId, newBook("allnew-새책")),
                HttpStatus.CONFLICT);
        assertThat(fail.get("code").asText()).isEqualTo("OVERDUE_EXISTS");
    }
}
