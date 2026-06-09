package kr.elice.shop.inventory.infrastructure;

import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import kr.elice.shop.inventory.domain.Reservation;
import kr.elice.shop.inventory.domain.ReservationRepository;
import org.springframework.stereotype.Repository;

/** 예약 저장소의 인메모리 어댑터입니다. 동시 접근에 견디도록 ConcurrentHashMap 으로 보관합니다. */
@Repository
public class InMemoryReservationRepository implements ReservationRepository {

    private final Map<String, Reservation> byId = new ConcurrentHashMap<>();

    @Override
    public Reservation save(Reservation reservation) {
        byId.put(reservation.id(), reservation);
        return reservation;
    }

    @Override
    public Optional<Reservation> findById(String id) {
        return Optional.ofNullable(byId.get(id));
    }

    @Override
    public List<Reservation> findByProductId(String productId) {
        return byId.values().stream()
                .filter(r -> r.productId().equals(productId))
                .toList();
    }
}
