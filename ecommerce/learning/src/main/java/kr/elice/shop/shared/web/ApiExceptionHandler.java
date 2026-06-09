package kr.elice.shop.shared.web;

import kr.elice.shop.shared.DomainException;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

/**
 * 전역 예외 핸들러입니다. 모든 도메인 예외를 ErrorCode 의 HTTP 상태와 {code, message} 본문으로
 * 일관되게 변환합니다. 덕분에 컨트롤러는 정상 흐름만 다루고 예외 변환을 신경 쓰지 않습니다.
 */
@RestControllerAdvice
public class ApiExceptionHandler {

    /** 오류 응답 본문입니다. code 는 ErrorCode 이름, message 는 사람이 읽는 설명입니다. */
    public record ErrorResponse(String code, String message) {}

    @ExceptionHandler(DomainException.class)
    public ResponseEntity<ErrorResponse> handleDomain(DomainException e) {
        return ResponseEntity.status(e.code().httpStatus())
                .body(new ErrorResponse(e.code().name(), e.getMessage()));
    }
}
