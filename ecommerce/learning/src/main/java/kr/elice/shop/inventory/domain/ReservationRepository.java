package kr.elice.shop.inventory.domain;

import java.util.List;
import java.util.Optional;

/** 예약 저장소 포트입니다. 가용분 계산을 위해 상품별 예약 조회를 제공합니다. */
public interface ReservationRepository {

    /** 예약을 저장하고 저장된 인스턴스를 돌려줍니다. */
    Reservation save(Reservation reservation);

    /** id 로 예약을 찾습니다. */
    Optional<Reservation> findById(String id);

    /** 한 상품에 걸린 모든 예약을 돌려줍니다. */
    List<Reservation> findByProductId(String productId);
}
