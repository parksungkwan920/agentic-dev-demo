# -*- coding: utf-8 -*-
"""화면 렌더: OTP 입력 화면. UI parity(스냅샷 일치)의 대상.

실제 강의 데모는 Playwright exactness gate로 픽셀 단위를 비교하지만,
이 환경(브라우저·compose 비가용)에서는 결정적 HTML 스냅샷 parity로 대체한다.
캐노니컬 스냅샷: sdd/04_verify/10_test/ui_parity/signup_otp.html (FR-6).
"""

# 화면 명세(signup.md)의 필수 요소: 제목·안내문·6자리 입력·확인 버튼.
SIGNUP_OTP_HTML = (
    '<main class="signup">'
    '<h1>인증번호 입력</h1>'
    '<p>이메일로 받은 6자리 인증번호를 입력하세요.</p>'
    '<input name="otp" inputmode="numeric" maxlength="6"/>'
    '<button type="submit">확인</button>'
    '</main>'
)

SCREENS = {"signup_otp": SIGNUP_OTP_HTML}


def render(screen):
    """화면 이름으로 캐노니컬 HTML을 반환한다."""
    return SCREENS[screen]
