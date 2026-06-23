package kr.elice.realfield.ingestion.client;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlElementWrapper;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlProperty;

import java.util.ArrayList;
import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
public record MolitResponse(
        @JacksonXmlProperty(localName = "body") Body body
) {
    public List<MolitAptTradeItem> items() {
        if (body == null || body.items() == null) return List.of();
        return body.items();
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public record Body(
            @JacksonXmlElementWrapper(localName = "items")
            @JacksonXmlProperty(localName = "item")
            List<MolitAptTradeItem> items
    ) {
        public Body {
            if (items == null) items = new ArrayList<>();
        }
    }
}
