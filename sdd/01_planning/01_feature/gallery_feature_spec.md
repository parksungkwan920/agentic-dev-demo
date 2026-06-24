# 갤러리 · Acceptance Criteria (EARS)

> 01_planning: 요구사항을 검증 가능한 EARS로 정제. 이 명세가 가드레일.
> 도메인 코드: GALLERY · **사진첩(PHOTO)과 동일한 공개범위/모델(PhotoService)을 재사용**한다.
> 사진첩과 분리된 별도 컨텐츠 보관함(인스턴스)으로, 실제 이미지(data URI)를 올린다.

**AC-1** When 홈피 주인이 갤러리에 이미지를 올리면, the system shall (owner, caption,
scope, image_uri, 시각) 항목을 저장한다. Where 업로더가 주인이 아니면 거부한다.

**AC-2** Where 항목의 공개범위가 ilchon이고 조회자가 일촌이 아니거나, private이고 조회자가
주인이 아니면, the system shall 그 항목을 목록에서 제외한다. (public은 누구에게나)

**AC-3** When 주인이 항목을 삭제하면, the system shall 제거한다. Where 삭제자가 주인이
아니면 거부한다.

**AC-4(이미지)** The 갤러리·사진첩 항목은 shall 실제 이미지(`image_uri`, data URI)를 가질 수
있고, 없으면 placeholder로 렌더한다. (도메인은 `image_uri` 필드로 보관, 인코딩은 base64)

## 검증 매핑

| AC | 테스트 |
| --- | --- |
| AC-1·AC-2·AC-3 | `tests/test_gallery.py::test_gallery_reuses_photo_model` (PhotoService 재사용) |
| AC-4 | `tests/test_gallery.py::test_image_uri_stored` |
| 회귀 | `tests/test_photo.py` (동일 모델 공유) |

> 사진첩(PHOTO)·다이어리(DIARY)도 동일하게 `image_uri`로 실제 이미지를 첨부할 수 있다.
> 이미지 업로드는 브라우저 `FileReader.readAsDataURL` → hidden 필드 → 일반 POST 경로
> (서버측 multipart 파싱 없음). 상세: `sdd/04_verify/02_screen/minihome_app.md`.
