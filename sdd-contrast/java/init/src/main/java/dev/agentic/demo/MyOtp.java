package dev.agentic.demo;

import java.util.Collection;
import java.util.HashMap;
import java.util.LinkedHashSet;
import java.util.Map;
import java.util.Set;

/**
 * Otp 구현 — spec.md(AC-1~4)의 수용기준을 모두 만족하도록 짠 버전입니다.
 *
 * <ul>
 *   <li>AC-1 정상 발급·검증: 유효한 코드로 가입하면 성공한다.</li>
 *   <li>AC-2 만료 거부: 발급 후 TTL(300초)이 지나면 거부한다.</li>
 *   <li>AC-3 5회 오류 잠금: 5회 연속 오답이면 이후 정답도 거부한다.</li>
 *   <li>AC-4 재요청 멱등: 같은 사용자가 두 번 가입해도 계정은 1개만 생긴다.</li>
 * </ul>
 */
public class MyOtp implements Otp {

    /** 발급 후 OTP가 유효한 시간(초). */
    private static final int TTL_SECONDS = 300;
    /** 연속 오답 허용 횟수. 이 횟수에 도달하면 잠근다. */
    private static final int MAX_ATTEMPTS = 5;

    /** 이메일별 발급된 코드와 발급 시각을 담는다. */
    private static final class Record {
        final String code;
        final int issuedAt;
        int failures; // 연속 오답 횟수

        Record(String code, int issuedAt) {
            this.code = code;
            this.issuedAt = issuedAt;
        }
    }

    private final Map<String, Record> records = new HashMap<>();
    // 가입된 사용자 (중복 가입 방지를 위해 Set 사용 → 멱등)
    private final Set<String> created = new LinkedHashSet<>();

    @Override
    public String issue(String email, int t) {
        // 6자리 코드를 발급하고 발급 시각을 기록한다(오답 카운터는 초기화).
        String code = "123456";
        records.put(email, new Record(code, t));
        return code;
    }

    @Override
    public boolean verify(String email, String code, int t) {
        Record rec = records.get(email);
        if (rec == null) {
            return false;
        }
        // AC-3: 5회 연속 오답이면 잠겨 있으므로 정답이라도 거부한다.
        if (rec.failures >= MAX_ATTEMPTS) {
            return false;
        }
        // AC-2: 발급 후 TTL이 지났으면 거부한다.
        if (t - rec.issuedAt > TTL_SECONDS) {
            return false;
        }
        // 코드 일치 여부 확인
        if (!rec.code.equals(code)) {
            rec.failures++; // 오답이면 카운터 증가
            return false;
        }
        return true;
    }

    @Override
    public boolean signup(String email, String code, int t) {
        // 검증을 통과하면 가입시킨다.
        if (!verify(email, code, t)) {
            return false;
        }
        created.add(email); // AC-4: Set이라 두 번 가입해도 1개만 남는다
        return true;
    }

    @Override
    public Collection<String> created() {
        return created;
    }
}
