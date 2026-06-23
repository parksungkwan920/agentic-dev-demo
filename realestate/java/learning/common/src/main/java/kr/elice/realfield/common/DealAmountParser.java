package kr.elice.realfield.common;

/**
 * data.go.kr 실거래가 API의 거래금액 파서입니다.
 *
 * <p>원천 {@code dealAmount} 는 만원 단위의 콤마 포함 문자열입니다(예: {@code " 82,500"}).
 * 이를 공백·콤마 제거 후 만원 정수로 만들고, 다시 원 단위(×10000)로 변환합니다.
 * 이 변환은 요구사항 AC-3의 핵심 정합 규칙이며, 수집 모듈이 적재 전에 반드시 거칩니다.
 */
public final class DealAmountParser {

    private DealAmountParser() {}

    /** 만원 단위 콤마 문자열을 원 단위 long으로 변환합니다. */
    public static long toWon(String rawDealAmount) {
        long manWon = toManWon(rawDealAmount);
        return manWon * 10_000L;
    }

    /** 만원 단위 콤마 문자열을 만원 정수로 변환합니다. */
    public static long toManWon(String rawDealAmount) {
        if (rawDealAmount == null || rawDealAmount.isBlank()) {
            throw new IllegalArgumentException("거래금액이 비어 있습니다.");
        }
        String digits = rawDealAmount.replace(",", "").trim();
        try {
            return Long.parseLong(digits);
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException("거래금액 파싱 실패: '" + rawDealAmount + "'", e);
        }
    }
}
