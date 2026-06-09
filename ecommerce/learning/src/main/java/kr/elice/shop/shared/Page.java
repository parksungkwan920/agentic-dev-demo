package kr.elice.shop.shared;

import java.util.List;

/**
 * 공용 페이징 값 객체입니다. page 는 1부터 시작합니다. 전체 목록을 받아 요청한 페이지만큼
 * 잘라 담고, 전체 개수와 총 페이지 수를 함께 돌려줘 목록 API 응답을 일관되게 만듭니다.
 */
public record Page<T>(List<T> items, long total, int page, int size, int pages) {

    /** 전체 목록을 1부터 시작하는 page 와 size 로 잘라 Page 로 만듭니다. */
    public static <T> Page<T> of(List<T> all, int page, int size) {
        int total = all.size();
        int pages = size <= 0 ? 0 : (int) Math.ceil((double) total / size);
        int from = Math.max(0, (page - 1) * size);
        int to = Math.min(total, from + size);
        List<T> slice = (size <= 0 || from >= total) ? List.of() : all.subList(from, to);
        return new Page<>(List.copyOf(slice), total, page, size, pages);
    }
}
