# 회귀 검증 범위 (retained)

| 표면 | 분류 | 검증 |
| --- | --- | --- |
| 미니홈피 메인·투데이 | direct | `test_minihome.py` |
| 일촌 신청/수락/해제/파도타기 | direct | `test_ilchon.py` |
| 도토리 충전/구매/선물/원장 | direct | `test_acorn.py` |
| 방명록 작성/삭제/비밀글/차단 | direct | `test_guestbook.py` |
| 사진첩 업로드/공개범위/대표/삭제 | direct | `test_photo.py` |
| 다이어리 작성/공개범위/삭제/연동 | direct | `test_diary.py` |
| 쪽지함 송수신/차단/읽음/연동 | direct | `test_message.py` |
| 게시판 작성/최신순/삭제/연동 | direct | `test_board.py` + `serve.py` 런타임 |
| 미니홈피 메인 화면 | direct | `test_screen_parity.py` + `run_ui_parity.py` |
| 공개범위 판정(visibility section/scope) | shared | 미니홈피·방명록·사진첩·다이어리가 공유 → 변경 시 전 도메인 회귀 |
| 멱등 저장소(idem) | shared | 도토리 충전·일촌 신청이 공유 → 변경 시 두 도메인 회귀 |
| 기존 인증/세션 | shared | `test_regression.py` |

## 선정 근거
- 미니홈피는 일촌·도토리·방명록을 조회로 조립하므로 하위 도메인 변경이 미니홈피 응답에 전파된다 → 미니홈피를 항상 회귀에 포함.
- `shared/visibility.py`·`shared/idem.py`는 다수 도메인이 공유하는 표면이므로, 이를 건드리면 회귀 범위를 공유 사용처 전체로 넓힌다.
- 도토리는 잔액 필드가 아닌 **원장 합 불변식**으로 검증해야 회귀에서 정합성 깨짐을 잡는다.
