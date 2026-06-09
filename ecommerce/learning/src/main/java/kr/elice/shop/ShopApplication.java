package kr.elice.shop;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/** 이커머스 모놀리식 애플리케이션 진입점입니다. 단일 부트 컨텍스트 안에 6개 컨텍스트를 담습니다. */
@SpringBootApplication
public class ShopApplication {

    public static void main(String[] args) {
        SpringApplication.run(ShopApplication.class, args);
    }
}
