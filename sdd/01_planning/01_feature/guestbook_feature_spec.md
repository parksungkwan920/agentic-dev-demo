# 방명록 · Acceptance Criteria (EARS)

> 01_planning: 요구사항을 검증 가능한 EARS로 정제. 이 명세가 가드레일.
> 도메인 코드: GUEST

**AC-1** When 방문자가 방명록을 남기면, the system shall (작성자, 홈피주인, 내용, 비밀여부, 시각)
글을 생성한다.

**AC-2** Where 글이 비밀글이면, the system shall 내용을 홈피 주인과 작성자에게만 노출하고,
그 외 조회자에게는 잠금 표시(내용 비공개)로 응답한다.

**AC-3** When 홈피 주인 또는 작성자가 자신의 권한 범위 글을 삭제하면, the system shall 삭제한다.
Where 삭제 요청자가 홈피 주인도 작성자도 아니면 삭제를 거부한다.

**AC-4** Where 작성자가 홈피 주인에게 차단된 사용자이면, the system shall 방명록 작성을
거부한다.

## 검증 매핑

| AC | 테스트 |
| --- | --- |
| AC-1 | `tests/test_guestbook.py::test_create_entry` |
| AC-2 | `tests/test_guestbook.py::test_secret_visible_to_owner_and_author_only` |
| AC-3 | `tests/test_guestbook.py::test_delete_permission` |
| AC-4 | `tests/test_guestbook.py::test_blocked_user_cannot_post` |
| 회귀 | `tests/test_regression.py` |
