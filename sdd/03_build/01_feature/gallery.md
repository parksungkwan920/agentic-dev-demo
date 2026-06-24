# 빌드 요약: 갤러리 + 실이미지 + 미니룸 (현재 상태)

> 03_build: 현재 구현된 범위·모듈·동작만 사실 기준으로 기록.

## 갤러리 (사진첩 모델 재사용)

- 새 도메인 코드 없음. `PhotoService` 두 번째 인스턴스(`serve.py`의 `gallery`)로 구현.
- 업로드(주인)·공개범위(public/ilchon/private)·대표·삭제가 사진첩과 동일하게 동작.
- 탭/라우트: `/?tab=gallery`, `/gallery/upload|cover|delete` (사진첩과 정규식 한 라우트로 분기).
- 메인 메뉴그리드 `갤러리 N`이 placeholder(0/0) → 실값으로.

## 실이미지 업로드 (사진첩·갤러리·다이어리)

- `Photo`/`DiaryEntry`에 `image_uri: str = ""` 기본값 추가(기존 테스트 비파괴).
- 업로드 경로: 브라우저 `<input type=file>` + JS `FileReader.readAsDataURL()`로 base64
  data URI 생성 → hidden `image_uri` 필드 → 일반 urlencoded POST. **서버측 multipart 파싱 없음**
  (base64는 ASCII라 인코딩 이슈 없음). 600KB 클라이언트 캡.
- 렌더: `image_uri` 있으면 `<img src=data:...>`, 없으면 placeholder(🖼️).

## 미니룸 (아이소메트릭 3D 픽셀아트)

- `render_miniroom()`이 인라인 SVG로 2:1 아이소메트릭 방을 그린다(의존성 0).
- 구성: 바닥 격자 타일 · 좌/우 벽 · 아치 창문 3 · 러그 · 가구(책장·책상+모니터·침대(프레임/이불/베개)
  ·화분·거울·협탁) · 미니미 캐릭터(주황 옷). `_iso()`/`_box()` 헬퍼로 좌표·명암 3면 생성.
- 메인화면 Mini Room 영역에 노출, "미니룸 벽지 ✎ 꾸미기" 태그.

## 아키텍처 준수

- 도메인 재사용(갤러리=PhotoService)으로 중복 코드 0. 이미지·SVG는 표현 계층(serve.py).
- 도메인 단위 테스트 49/49 PASS(갤러리 3 추가). 이미지/미니룸은 렌더라 도메인 불변.
