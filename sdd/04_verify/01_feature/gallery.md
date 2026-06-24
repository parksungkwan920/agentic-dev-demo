# 검증 요약: 갤러리 + 실이미지 (retained)

> 04_verify: command-level 증거 기준.

## 게이트 결과

- `python proof/run_proof.py` → exit 0, **49/49 PASS** (기존 46 + 갤러리 3).

## EARS AC ↔ 테스트

| AC | 테스트 |
| --- | --- |
| GALLERY AC-1~AC-3 (재사용) | `test_gallery.py::test_gallery_reuses_photo_model` |
| GALLERY AC-4 (image_uri 보관) | `test_gallery.py::test_image_uri_stored` |
| image_uri 기본값 | `test_gallery.py::test_image_uri_default_empty` |
| 회귀(사진첩 모델) | `test_photo.py` (동일 PhotoService) |

## 런타임(이용성) 검증 (HTTP)

- 갤러리 탭 placeholder 제거, `/gallery/upload`(image_uri=data URI) → 실 `<img src=data:image...>` 렌더, 개수 반영.
- 사진첩 실이미지 업로드 → `<img>` 렌더.
- 다이어리 이미지 첨부 → `.dimg` 렌더.
- 메인 메뉴그리드 갤러리 실값 표시.

## 잔여 리스크

- 이미지 인메모리(data URI), 600KB 캡, 영속성 없음.
- 갤러리는 별도 인스턴스지만 도메인 코드는 사진첩과 동일(의도된 재사용).
- 미니룸은 정적 아이소메트릭 SVG — 실제 가구 배치/구매(아이템샵)는 deferred.
