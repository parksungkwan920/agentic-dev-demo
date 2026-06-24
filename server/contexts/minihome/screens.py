# -*- coding: utf-8 -*-
"""화면 렌더: 미니홈피 메인. UI parity(스냅샷 일치)의 대상.

레퍼런스 auth 데모와 동일하게, 브라우저 비가용 환경에서는
결정적 HTML 스냅샷 parity로 Playwright exactness gate를 대체한다.

뼈대는 싸이월드 클래식 미니홈피 구조(상단 TODAY/TOTAL · 좌 프로필 ·
중앙 Updated news/Mini Room/방명록 · 우 세로탭)를 시맨틱하게 표현한다.
시각 스타일(CSS)·실데이터 바인딩은 데모 렌더러(99_toolchain)가 담당한다.
"""

MINIHOME_MAIN_HTML = (
    '<main class="minihome">'
    '<div class="cy-top">'
    '<span class="counter"><span class="today">TODAY</span>'
    '<span class="total">TOTAL</span></span>'
    '<h1 class="cy-title">사이좋은 사람들</h1>'
    '</div>'
    '<aside class="profile">'
    '<div class="avatar"></div>'
    '<div class="acts">EDIT | HISTORY</div>'
    '</aside>'
    '<section class="content">'
    '<div class="bar">Updated news</div>'
    '<nav class="menu">'
    '<a href="#diary">다이어리</a>'
    '<a href="#photo">사진첩</a>'
    '<a href="#gallery">갤러리</a>'
    '<a href="#board">게시판</a>'
    '</nav>'
    '<div class="miniroom"><span class="bar">Mini Room</span></div>'
    '<section class="friends"><h3>What friends say</h3></section>'
    '</section>'
    '<nav class="tabs">'
    '<a href="#profile">프로필</a>'
    '<a href="#diary">다이어리</a>'
    '<a href="#photo">사진첩</a>'
    '<a href="#gallery">갤러리</a>'
    '<a href="#board">게시판</a>'
    '<a href="#guestbook">방명록</a>'
    '<a href="#fav">즐겨찾기</a>'
    '</nav>'
    '</main>'
)

SCREENS = {"minihome_main": MINIHOME_MAIN_HTML}


def render(screen):
    return SCREENS[screen]
