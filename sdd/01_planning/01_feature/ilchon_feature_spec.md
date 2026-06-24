# 일촌 · Acceptance Criteria (EARS)

> 01_planning: 요구사항을 검증 가능한 EARS로 정제. 이 명세가 가드레일.
> 도메인 코드: ILCHON

**AC-1** When 사용자가 일촌을 신청하면, the system shall (요청자, 대상, 호칭쌍, 상태=pending)
신청을 생성한다.

**AC-2** Where 일촌 신청에 호칭쌍(나→상대, 상대→나)이 모두 채워져 있지 않으면,
the system shall 신청을 거부한다.

**AC-3** While 신청이 pending일 때, when 대상이 수락하면, the system shall 양방향(상호)
일촌 관계를 맺고 상태를 accepted로 전이한다.

**AC-4** When 이미 pending이거나 accepted인 대상에게 일촌이 재신청되면, the system shall
중복 관계를 만들지 않는다(멱등).

**AC-5** When 사용자가 일촌을 끊으면, the system shall 양쪽 방향의 관계를 모두 해제한다.

**AC-6** When 사용자가 파도타기를 요청하면, the system shall 사용자의 일촌의 일촌 중
(본인·기존 일촌 제외) 무작위 한 명의 미니홈피로 이동 대상을 반환한다.

## 검증 매핑

| AC | 테스트 |
| --- | --- |
| AC-1 | `tests/test_ilchon.py::test_request_creates_pending` |
| AC-2 | `tests/test_ilchon.py::test_request_requires_both_nicknames` |
| AC-3 | `tests/test_ilchon.py::test_accept_creates_mutual` |
| AC-4 | `tests/test_ilchon.py::test_duplicate_request_idempotent` |
| AC-5 | `tests/test_ilchon.py::test_break_removes_both_directions` |
| AC-6 | `tests/test_ilchon.py::test_wave_returns_friend_of_friend` |
| 회귀 | `tests/test_regression.py` |
