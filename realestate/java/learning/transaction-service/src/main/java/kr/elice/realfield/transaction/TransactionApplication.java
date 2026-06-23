package kr.elice.realfield.transaction;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/** 거래원장 서비스입니다. 정규화된 실거래를 자연키로 멱등 적재(write model)합니다. */
@SpringBootApplication
public class TransactionApplication {
    public static void main(String[] args) {
        SpringApplication.run(TransactionApplication.class, args);
    }
}
