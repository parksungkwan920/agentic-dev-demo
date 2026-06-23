package kr.elice.realfield.ingestion.client;

import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlProperty;

public record MolitAptTradeItem(
        @JacksonXmlProperty(localName = "sggCd") String sggCd,
        @JacksonXmlProperty(localName = "umdNm") String umdNm,
        @JacksonXmlProperty(localName = "jibun") String jibun,
        @JacksonXmlProperty(localName = "aptNm") String aptNm,
        @JacksonXmlProperty(localName = "excluUseAr") String excluUseAr,
        @JacksonXmlProperty(localName = "dealYear") String dealYear,
        @JacksonXmlProperty(localName = "dealMonth") String dealMonth,
        @JacksonXmlProperty(localName = "dealDay") String dealDay,
        @JacksonXmlProperty(localName = "dealAmount") String dealAmount,
        @JacksonXmlProperty(localName = "floor") String floor,
        @JacksonXmlProperty(localName = "buildYear") String buildYear,
        @JacksonXmlProperty(localName = "dealingGbn") String dealingGbn,
        @JacksonXmlProperty(localName = "cdealType") String cdealType,
        @JacksonXmlProperty(localName = "cdealDay") String cdealDay
) {
}
