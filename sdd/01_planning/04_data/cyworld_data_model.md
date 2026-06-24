# 데이터 모델 (초안)

> 관계(일촌 그래프)·통화(도토리 원장)가 있어 auth 데모보다 데이터 설계를 명시한다.
> 데모는 인메모리 dict/list로 시작하되, 아래 엔티티 경계는 RDB 이행 시에도 유지한다.

## 엔티티

### User / Minihome
| 필드 | 타입 | 비고 |
| --- | --- | --- |
| user_id | str | 식별자(불투명) |
| minimi_id | str | 미니미/미니룸 표시용 |
| today_count | int | 오늘 방문수(일자 경계서 리셋) |
| total_visits | int | 누적 방문수 |
| private_sections | set[str] | 비공개 섹션명(예: "diary") |

### Ilchon (일촌 관계)
| 필드 | 타입 | 비고 |
| --- | --- | --- |
| requester / target | str | 신청자 / 대상 |
| nick_req_to_target | str | 나→상대 호칭 (필수) |
| nick_target_to_req | str | 상대→나 호칭 (필수) |
| status | enum | pending / accepted |
- 수락 시 양방향 관계를 표현(상호). 멱등 키: `(requester, target)` 정렬쌍.

### AcornLedger (도토리 원장)
| 필드 | 타입 | 비고 |
| --- | --- | --- |
| entry_id | str | 멱등 키(결제/요청 id) |
| user_id | str | 잔액 귀속 대상 |
| amount | int | +credit / -debit |
| kind | enum | charge / purchase / gift_in / gift_out |
| ref | str | 선물 상대·아이템 등 참조 |
- **불변식**: `balance(user) == sum(amount where user_id == user)`.
- 선물은 `gift_out`/`gift_in` 두 항목을 한 트랜잭션으로 기록(원자성).

### GuestbookEntry (방명록)
| 필드 | 타입 | 비고 |
| --- | --- | --- |
| entry_id | str | 식별자 |
| owner_id | str | 홈피 주인 |
| author_id | str | 작성자 |
| content | str | 내용 |
| secret | bool | 비밀글 여부 |
| created_at | datetime | 작성 시각 |
- 차단: `owner.blocked: set[user_id]` (작성 거부 판정에 사용).

## 핵심 불변식 (검증 훅)

1. 도토리: 임의 시점 `잔액 = sum(ledger)` — `test_acorn.py::test_balance_equals_ledger_sum`.
2. 일촌: accepted면 양방향 동시 존재/해제 — `test_ilchon.py`.
3. 미니홈피: 주인 본인 방문은 카운트 제외 — `test_minihome.py`.
