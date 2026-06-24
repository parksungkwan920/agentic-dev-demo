# 01_planning: INDEX (1단 진입점)

> 폴더를 열면 이 INDEX가 먼저 보인다: 어떤 명세가 있고 어디까지 됐는지 1단으로.
> 핵심 슬라이스는 구현·검증까지 완료(proof 25/25 PASS).
> 05_operate(배포)는 범위 밖 — 롤아웃 미수행.

## Feature

| 영역 | 파일 | 상태 |
| --- | --- | --- |
| feature · 미니홈피 | `01_feature/minihome_feature_spec.md` | 구현·검증 완료 |
| feature · 일촌 | `01_feature/ilchon_feature_spec.md` | 구현·검증 완료 |
| feature · 도토리 | `01_feature/acorn_feature_spec.md` | 구현·검증 완료 |
| feature · 방명록 | `01_feature/guestbook_feature_spec.md` | 구현·검증 완료 |
| feature · 사진첩 | `01_feature/photo_feature_spec.md` | 구현·검증 완료 |
| feature · 다이어리 | `01_feature/diary_feature_spec.md` | 구현·검증 완료 |
| feature · 쪽지함 | `01_feature/message_feature_spec.md` | 구현·검증 완료 |
| feature · 게시판 | `01_feature/board_feature_spec.md` | 구현·검증 완료 (인터랙티브 서버) |
| feature · 갤러리 | `01_feature/gallery_feature_spec.md` | 구현·검증 완료 (사진첩 모델 재사용·실이미지) |
| feature · 즐겨찾기 | `01_feature/favorite_feature_spec.md` | 구현·검증 완료 (본인 전용 북마크) |
| feature · BGM | `01_feature/bgm_feature_spec.md` | 구현·검증 완료 (도토리 구매·Web Audio 재생) |
| feature · 미니룸 아이템샵 | `01_feature/shop_feature_spec.md` | 구현·검증 완료 (도토리 구매·미니룸 배치) |

## 횡단 영역

| 영역 | 파일 | 상태 |
| --- | --- | --- |
| architecture | `03_architecture/cyworld_architecture.md` | 초안 |
| data | `04_data/cyworld_data_model.md` | 초안 |

## EARS 가드레일 요약

- 미니홈피: 투데이 카운트(본인 제외) · 공개범위(일촌/본인) · 화면 parity
- 일촌: 상호 관계 · 호칭쌍 필수 · 멱등 신청 · 파도타기
- 도토리: 원장 정합(`잔액 = sum(ledger)`) · 원자적 선물 · 멱등 충전
- 방명록: 비밀글 가시성 · 삭제 권한 · 차단
- 사진첩: 업로드(주인) · 공개범위(public/ilchon/private) · 대표사진 · 미니홈피 연동
- 다이어리: 작성(주인) · 공개범위(public/ilchon/private) · 섹션 비공개 + 글별 scope 연동
- 쪽지함: 1:1 송수신 · 차단(방명록 공유) · 읽음 권한 · 본인 전용 카운트
- 게시판: 작성 · 최신순 목록 · 삭제(작성자/주인) · 차단 — **인터랙티브 서버(`serve.py`)로 실제 이용 가능**
- 갤러리: 사진첩 모델(PhotoService) 재사용 · 실이미지(data URI) 업로드 — 사진첩·다이어리도 이미지 첨부
- 미니룸: 아이소메트릭 3D 픽셀아트 방(인라인 SVG) — 가구·벽지·창문·미니미
- BGM: 도토리로 곡 구매(acorn 소비처) · 보유/현재곡 · Web Audio API 멜로디 재생(음원 0)
- 미니룸 아이템샵: 도토리로 가구 구매(acorn 소비처) · 인벤토리 · SVG 방에 배치
- **deferred 전부 소진** — 핵심 슬라이스 + 확장 9개 도메인 구현 완료
