package kr.elice.realfield.common;

/**
 * 정규화된 아파트 실거래 한 건입니다. 원천(data.go.kr)의 XML item을 표준 스키마로 변환한 결과이며,
 * 수집·거래원장·분석 모듈이 공유하는 계약(contract)입니다.
 *
 * <p>금액은 원 단위 long으로 보관합니다. 원천의 거래금액은 만원 단위 콤마 문자열이므로
 * {@link DealAmountParser}로 변환해 채웁니다. {@code canceled} 가 true 이면 해제된 거래이며
 * 시세 집계에서 제외합니다(요구사항 AC-3).
 */
public record AptTransaction(
        String sggCd,        // 법정동 시군구코드 (5자리)
        String umdNm,        // 법정동(읍면동)명
        String aptNm,        // 단지명
        double exclusiveArea,// 전용면적(㎡)
        int floor,           // 층
        int buildYear,       // 건축년도
        int dealYear,
        int dealMonth,
        int dealDay,
        long dealAmountWon,  // 거래금액 (원 단위)
        boolean canceled     // 해제여부 (cdealType == "O")
) {
    /** 자연키: 동일 거래를 멱등 적재하기 위한 식별자입니다(요구사항 AC-4). */
    public String naturalKey() {
        return String.join("|",
                sggCd, umdNm, aptNm,
                String.valueOf(exclusiveArea), String.valueOf(floor),
                String.valueOf(dealYear), String.valueOf(dealMonth), String.valueOf(dealDay),
                String.valueOf(dealAmountWon));
    }

    /** ㎡당 단가(원)를 계산합니다. 전용면적이 0이면 0을 반환합니다. */
    public long pricePerSquareMeter() {
        if (exclusiveArea <= 0) return 0L;
        return Math.round(dealAmountWon / exclusiveArea);
    }
}
