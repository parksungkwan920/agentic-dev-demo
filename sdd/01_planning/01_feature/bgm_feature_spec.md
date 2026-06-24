# BGM · Acceptance Criteria (EARS)

> 01_planning: 요구사항을 검증 가능한 EARS로 정제. 이 명세가 가드레일.
> 도메인 코드: BGM · 도토리(acorn) 소비처. 곡 카탈로그에서 구매·보유·현재곡 설정.

**AC-1** When 주인이 곡을 구매하고(미보유·잔액 충분) the system shall 도토리를 곡 가격만큼
차감하고 해당 곡을 보유에 추가한다.

**AC-2** If 구매 시 잔액이 부족하면, then the system shall 구매를 거부하고 잔액·보유를
변경하지 않는다.

**AC-3** When 이미 보유한 곡을 재구매하면, the system shall 거부하고 도토리를 중복 차감하지
않는다.

**AC-4** When 주인이 현재 BGM을 설정하면, the system shall 보유한 곡만 현재곡으로 둔다
(미보유 곡 설정 거부).

**AC-5** The system shall 모든 구매를 acorn 원장으로 처리해 `잔액 = sum(ledger)` 불변식을
유지한다. 구매마다 유일한 entry_id를 사용한다.

## 검증 매핑

| AC | 테스트 |
| --- | --- |
| AC-1 | `tests/test_bgm.py::test_buy_deducts_and_grants` |
| AC-2 | `tests/test_bgm.py::test_insufficient_rejected` |
| AC-3 | `tests/test_bgm.py::test_already_owned_rejected` |
| AC-4 | `tests/test_bgm.py::test_set_current_owned_only` |
| AC-5 | `tests/test_bgm.py::test_balance_equals_ledger` |
| 재생 | `serve.py` 런타임(Web Audio API ▶ 버튼, 사용자 제스처) |

> 재생은 음원 파일 없이 Web Audio API 오실레이터로 곡별 멜로디를 합성한다(의존성 0).
> 브라우저 자동재생 정책상 ▶ 버튼 클릭(사용자 제스처)으로만 시작한다.
