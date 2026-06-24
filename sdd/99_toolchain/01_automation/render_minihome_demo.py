# -*- coding: utf-8 -*-
"""미니홈피 데모 렌더러: 구현한 도메인 서비스를 실제 시드 데이터로 구동해
브라우저로 볼 수 있는 완전한 HTML 페이지를 생성한다.

- 도메인 로직(투데이 카운트·일촌 수·도토리 잔액·방명록 가시성)이 실제로 동작한 결과를
  싸이월드 클래식 미니홈피 레이아웃(3단: 좌 프로필 / 중앙 컨텐츠 / 우 세로탭)에 바인딩한다.
- 출력: tmp/minihome_demo.html (+ 옵션: 기본 브라우저로 열기)
"""
import html
import pathlib
import sys
import webbrowser

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from server.contexts.acorn.acorn import AcornService  # noqa: E402
from server.contexts.diary.diary import DiaryService  # noqa: E402
from server.contexts.guestbook.guestbook import GuestbookService  # noqa: E402
from server.contexts.ilchon.ilchon import IlchonService  # noqa: E402
from server.contexts.message.message import MessageService  # noqa: E402
from server.contexts.minihome.minihome import MinihomeService  # noqa: E402
from server.contexts.photo.photo import PhotoService  # noqa: E402

OWNER = "과니"


def build_payload():
    """시드 데이터로 4개 도메인을 구동하고 미니홈피 메인 페이로드를 조립한다."""
    ilchon = IlchonService()
    acorn = AcornService(ilchon=ilchon)
    gb = GuestbookService(clock=lambda: 0.0)
    photo = PhotoService(ilchon=ilchon, clock=lambda: 0.0)
    diary = DiaryService(ilchon=ilchon, clock=lambda: 0.0)
    message = MessageService(clock=lambda: 0.0)
    home = MinihomeService(ilchon=ilchon, acorn=acorn, guestbook=gb,
                           photo=photo, diary=diary, message=message)

    # 일촌: 신청 → 수락 (상호)
    for friend, mine, theirs in [
        ("병익", "베프", "단짝"),
        ("효정", "동네친구", "동네친구"),
        ("계희", "회사동기", "회사동기"),
    ]:
        ilchon.request(OWNER, friend, mine, theirs)
        ilchon.accept(OWNER, friend)

    # 도토리: 충전 후 미니룸 아이템 구매
    acorn.charge(OWNER, 1500, entry_id="charge-1")
    acorn.purchase(OWNER, 300, entry_id="buy-room", ref="미니룸 벽지")

    # 방명록: 공개글 + 비밀글
    gb.post(OWNER, "병익", "오랜만에 미니홈피 왔다 간다~ 일촌평 남겨줘!")
    gb.post(OWNER, "효정", "BGM 뭐야? 노래 좋다 ♪")
    gb.post(OWNER, "계희", "우리끼리 비밀 얘기...", secret=True)

    # 사진첩: 공개범위별 사진 + 대표사진 지정
    photo.upload(OWNER, OWNER, "제주도 바다", scope="public")
    photo.upload(OWNER, OWNER, "일촌 모임", scope="ilchon")
    photo.upload(OWNER, OWNER, "셀카 (나만보기)", scope="private")
    cover_id = photo.list_for(OWNER, OWNER)[0].photo_id
    photo.set_cover(OWNER, cover_id, OWNER)

    # 다이어리: 공개범위별 글
    diary.write(OWNER, OWNER, "첫 일기", "미니홈피 시작!", mood="😊", scope="public")
    diary.write(OWNER, OWNER, "일촌만 보는 글", "우리끼리 얘기", mood="🤫", scope="ilchon")
    diary.write(OWNER, OWNER, "혼자 쓰는 글", "비밀일기", mood="😴", scope="private")

    # 쪽지함: 받은 쪽지 (일부 읽음)
    message.send("병익", OWNER, "오늘 미니홈피 놀러왔어!")
    message.send("효정", OWNER, "BGM 추천 좀~")
    message.send("계희", OWNER, "주말에 보자")
    message.read(message.inbox(OWNER)[0].msg_id, OWNER)  # 1개만 읽음 → 안읽음 2

    # 미니홈피 비공개 섹션 설정
    home.set_private(OWNER, {"diary"})

    # 방문 발생 (투데이/토탈 카운트) — 본인 방문은 카운트되지 않음
    for visitor in ["병익", "효정", "계희", "지나가던손님", "병익", OWNER]:
        home.open(OWNER, visitor)

    # 주인 시점으로 메인 조립 (도토리 잔액·비밀글 내용까지 보임)
    return home.main(OWNER, OWNER)


def render_html(p) -> str:
    e = html.escape
    owner = e(p["owner_id"])

    # --- 방명록 (What friends say) ---
    rows = []
    for v in reversed(p["recent_guestbook"]):  # 최신글 위로
        author = e(v.author_id)
        if v.locked:
            body = '<span class="locked">🔒 비밀글입니다</span>'
        else:
            body = e(v.content or "")
            if v.secret:
                body = f'<span class="secret-badge">비밀</span> {body}'
        rows.append(
            f'<li class="gb-item"><b class="gb-author">{author}</b>'
            f'<span class="gb-body">{body}</span></li>'
        )
    gb_html = "\n".join(rows) or '<li class="gb-empty">아직 방명록이 없어요.</li>'

    # --- 중앙 메뉴 카운트: 다이어리는 실제 sections 기반, 나머지는 deferred(미구현) ---
    sections = p.get("sections", [])
    diary_count = p.get("diary_count", 0)  # 조회자 기준 보이는 글 수 (실값)
    diary_lock = "🔒" if "diary" in sections else ""
    acorn_balance = p.get("acorn_balance")
    photo_count = p.get("photo_count", 0)
    photo_cover = p.get("photo_cover")
    msg_unread = p.get("message_unread")
    msg_total = p.get("message_total")
    msg_cnt = f"{msg_unread}/{msg_total}" if msg_unread is not None else "-"

    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{owner}님의 미니홈피</title>
<style>
  * {{ box-sizing:border-box; }}
  body {{ margin:0; padding:20px; background:#6f9fc8;
         font-family:"맑은 고딕","Malgun Gothic",Dotum,sans-serif; font-size:12px; color:#333; }}
  .cy {{ width:840px; margin:0 auto; background:#fff; border:1px solid #356; border-radius:4px;
        box-shadow:0 8px 30px rgba(0,0,0,.3); overflow:hidden; }}

  /* 상단바: TODAY/TOTAL · 타이틀 · URL */
  .cy-top {{ display:flex; align-items:center; gap:14px; padding:7px 12px;
            background:linear-gradient(#fafdff,#dcebf7); border-bottom:1px solid #9cc3df; }}
  .counter {{ font-weight:bold; }}
  .counter .t-today {{ color:#d23; }} .counter .t-total {{ color:#558; }}
  .counter b {{ font-size:13px; }}
  .cy-title {{ flex:1; text-align:center; font-size:15px; font-weight:bold; color:#2c5f86;
              letter-spacing:1px; }}
  .cy-url {{ font-size:11px; color:#789; }}

  .cy-body {{ display:flex; }}

  /* 좌측 프로필 패널 */
  .col-left {{ width:172px; background:#eef5fb; border-right:1px solid #cfe0ee; padding:12px; }}
  .today-is {{ font-size:11px; color:#d23; margin-bottom:6px; }}
  .today-is b {{ color:#333; }}
  .avatar {{ height:150px; border:1px solid #e6b9cd; border-radius:5px; position:relative; overflow:hidden;
            background:linear-gradient(#cfefff,#bfe6ff 55%,#a9d49a 55%,#9ccb8d); }}
  .avatar .doll {{ position:absolute; left:50%; bottom:8px; transform:translateX(-50%);
                  width:54px; height:84px; background:#ffd23f; border-radius:26px 26px 12px 12px;
                  box-shadow:inset -5px -5px rgba(0,0,0,.08); }}
  .avatar .doll::before {{ content:""; position:absolute; top:13px; left:15px; width:7px; height:7px;
                          background:#333; border-radius:50%; box-shadow:16px 0 #333; }}
  .avatar .sun {{ position:absolute; top:8px; right:10px; font-size:18px; }}
  .pf-title {{ margin-top:10px; font-weight:bold; color:#2c5f86; text-align:center; }}
  .pf-sub {{ text-align:center; color:#888; font-size:11px; }}
  .pf-acts {{ margin-top:8px; text-align:center; font-size:11px; color:#789; }}
  .pf-acts a {{ color:#789; text-decoration:none; }}
  .pf-logo {{ margin-top:12px; text-align:center; font-weight:bold; color:#2c5f86; }}
  .pf-mail {{ text-align:center; color:#9ab; font-size:11px; }}
  .pf-cover {{ margin-top:12px; background:#f2f8ff; border:1px solid #cfe0ee; border-radius:5px;
              padding:6px; text-align:center; font-size:11px; color:#557; }}
  .pf-cover b {{ display:block; color:#2c5f86; margin:2px 0; }}
  .pf-cnt {{ color:#9ab; }}
  .pf-acorn {{ margin-top:10px; background:#fff6e2; border:1px solid #f0d59a; border-radius:5px;
              padding:6px; text-align:center; }}
  .pf-acorn b {{ color:#c87f10; }}
  .pf-ilchon {{ margin-top:8px; text-align:center; color:#2c5f86; }}

  /* 중앙 컨텐츠 */
  .col-mid {{ flex:1; padding:12px 14px; }}
  .bar {{ background:linear-gradient(#eaf4fc,#d4e8f7); border:1px solid #b6d3e8; border-radius:3px;
         padding:4px 9px; font-weight:bold; color:#2c5f86; }}
  .bar small {{ color:#9ab; font-weight:normal; margin-left:6px; }}
  .menu-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:3px 20px; margin:10px 4px 4px; }}
  .menu-grid a {{ display:flex; justify-content:space-between; padding:3px 4px; text-decoration:none;
                 color:#2c5f86; border-bottom:1px dotted #d6e3ee; }}
  .menu-grid a.off {{ color:#aab; }}
  .menu-grid .cnt {{ color:#d23; }}
  .menu-grid a.off .cnt {{ color:#bbc; }}

  .miniroom-bar {{ margin-top:14px; display:flex; justify-content:space-between; align-items:center; }}
  .miniroom-bar .mr-r {{ color:#c87f10; font-size:11px; }}
  .miniroom {{ margin-top:6px; height:180px; border:1px solid #cdb; border-radius:4px; position:relative;
              background:linear-gradient(#dff0ff 60%,#caa97f 60%); overflow:hidden; }}
  .miniroom .win {{ position:absolute; top:18px; width:46px; height:60px; background:#bfe3ff;
                   border:3px solid #fff; border-radius:3px; box-shadow:0 0 0 1px #9cc; }}
  .miniroom .win.w1 {{ left:40px; }} .miniroom .win.w2 {{ left:110px; }}
  .miniroom .furni {{ position:absolute; bottom:14px; font-size:30px; }}
  .miniroom .bed {{ left:24px; }} .miniroom .desk {{ left:120px; }}
  .miniroom .cat {{ right:120px; bottom:18px; font-size:22px; }}
  .miniroom .me {{ right:46px; bottom:10px; font-size:30px; }}
  .miniroom .tag {{ position:absolute; top:6px; right:8px; background:#fff; border:1px solid #cdb;
                   border-radius:3px; padding:1px 6px; color:#c87f10; }}
  .room-acts {{ margin-top:6px; text-align:center; font-size:11px; color:#789; }}
  .room-acts span {{ margin:0 6px; }}

  .friends {{ margin-top:16px; }}
  .friends h3 {{ margin:0 0 6px; font-size:12px; color:#2c5f86; }}
  .gb {{ list-style:none; margin:0; padding:0; }}
  .gb-item {{ border-bottom:1px dashed #dde6ee; padding:7px 2px; display:flex; gap:9px; }}
  .gb-author {{ min-width:58px; color:#2c5f86; }}
  .gb-body {{ flex:1; }}
  .secret-badge {{ background:#c0392b; color:#fff; border-radius:3px; padding:0 5px; font-size:10px; }}
  .locked {{ color:#999; font-style:italic; }}
  .gb-empty {{ color:#999; padding:8px; }}

  /* 우측 세로 탭 */
  .col-right {{ width:64px; background:#dcebf7; border-left:1px solid #b6d3e8; padding-top:8px; }}
  .tab {{ display:block; margin:4px 6px; padding:7px 0; text-align:center; text-decoration:none;
         background:linear-gradient(#fbfdff,#cfe2f2); border:1px solid #a9c8e0; border-radius:3px;
         color:#2c5f86; font-size:11px; }}
  .tab.on {{ background:#2c5f86; color:#fff; border-color:#234; }}
  .foot {{ text-align:center; font-size:11px; color:#9bb; padding:9px; border-top:1px solid #e3eef6; }}
</style>
</head>
<body>
  <div class="cy">
    <div class="cy-top">
      <span class="counter">
        <span class="t-today">TODAY <b>{p['today']}</b></span>
        &nbsp;|&nbsp;
        <span class="t-total">TOTAL <b>{p['total']}</b></span>
      </span>
      <span class="cy-title">사이좋은 사람들</span>
      <span class="cy-url">http://www.cyworld.com/{owner}</span>
    </div>

    <div class="cy-body">
      <!-- 좌측 프로필 -->
      <aside class="col-left">
        <div class="today-is">TODAY IS... <b>행복</b></div>
        <div class="avatar"><span class="sun">☀️</span><div class="doll"></div></div>
        <div class="pf-title">{owner}</div>
        <div class="pf-sub">사이좋은 사람들 · 싸이월드</div>
        <div class="pf-acts"><a href="#edit">✎ EDIT</a> | <a href="#history">⟳ HISTORY</a></div>
        <div class="pf-cover">📷 대표사진<br><b>{e(photo_cover) if photo_cover else '없음'}</b>
          <span class="pf-cnt">사진첩 {photo_count}장</span></div>
        <div class="pf-acorn">🌰 도토리 <b>{acorn_balance if acorn_balance is not None else '-'}</b></div>
        <div class="pf-ilchon">👥 일촌 <b>{p['ilchon_count']}</b>명</div>
        <div class="pf-logo">CYWORLD ②</div>
        <div class="pf-mail">{owner}@cyworld.com</div>
      </aside>

      <!-- 중앙 컨텐츠 -->
      <main class="col-mid">
        <div class="bar">Updated news <small>TODAY STORY</small></div>
        <div class="menu-grid">
          <a href="#diary">다이어리 {diary_lock} <span class="cnt">{diary_count}</span></a>
          <a href="#note">쪽지함 <span class="cnt">{msg_cnt}</span></a>
          <a href="#photo">사진첩 <span class="cnt">{photo_count}</span></a>
          <a href="#gallery" class="off" title="예정(deferred)">갤러리 <span class="cnt">0/0</span></a>
          <a href="#board" class="off" title="예정(deferred)">게시판 <span class="cnt">0/99</span></a>
          <a href="#find" class="off" title="예정(deferred)">친구찾기 <span class="cnt">0/0</span></a>
        </div>

        <div class="miniroom-bar">
          <div class="bar" style="flex:1">Mini Room <small>EXPRESS YOURSELF</small></div>
          <div class="mr-r">와플준비중</div>
        </div>
        <div class="miniroom">
          <span class="tag">미니룸 벽지</span>
          <span class="win w1"></span><span class="win w2"></span>
          <span class="furni bed">🛏️</span>
          <span class="furni desk">🖥️</span>
          <span class="furni cat">🐱</span>
          <span class="furni me">🧍</span>
        </div>
        <div class="room-acts">
          <span>◀ 미니룸 ▶</span><span>일촌사진트리</span><span>미니미 달showroom</span>
        </div>

        <section class="friends">
          <h3>What friends say <small>방명록</small></h3>
          <ul class="gb">
{gb_html}
          </ul>
        </section>
      </main>

      <!-- 우측 세로 탭 -->
      <nav class="col-right">
        <a href="#profile" class="tab on">프로필</a>
        <a href="#diary" class="tab">다이어리</a>
        <a href="#photo" class="tab">사진첩</a>
        <a href="#gallery" class="tab">갤러리</a>
        <a href="#board" class="tab">게시판</a>
        <a href="#guestbook" class="tab">방명록</a>
        <a href="#fav" class="tab">즐겨찾기</a>
      </nav>
    </div>
    <div class="foot">minimi: {e(p['minimi_id'])} · 본인 시점 렌더 (도토리·비밀글 노출) · SDD 데모 · 도메인 로직 실동작</div>
  </div>
</body>
</html>"""


def main():
    payload = build_payload()
    out = ROOT / "tmp" / "minihome_demo.html"
    out.write_text(render_html(payload), encoding="utf-8")
    print(f"[demo] payload={payload}")
    print(f"[demo] wrote {out}")
    if "--open" in sys.argv:
        webbrowser.open(out.as_uri())
        print("[demo] opened in default browser")
    return 0


if __name__ == "__main__":
    sys.exit(main())
