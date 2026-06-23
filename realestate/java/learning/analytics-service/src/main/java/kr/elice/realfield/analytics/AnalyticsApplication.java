package kr.elice.realfield.analytics;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.loadbalancer.LoadBalanced;
import org.springframework.context.annotation.Bean;
import org.springframework.web.reactive.function.client.WebClient;

/** 분석 서비스입니다. 거래원장과 분리된 read model에서 시세 통계를 제공합니다(CQRS 읽기 측). */
@SpringBootApplication
public class AnalyticsApplication {
    public static void main(String[] args) {
        SpringApplication.run(AnalyticsApplication.class, args);
    }

    /** 디스커버리 기반 로드밸런싱 WebClient. lb://transaction-service 로 거래원장을 조회합니다. */
    @Bean
    @LoadBalanced
    WebClient.Builder loadBalancedWebClientBuilder() {
        return WebClient.builder();
    }
}
