# -*- coding: utf-8 -*-
"""싸이월드 미니홈피 — 실행 가능한 통합 인터랙티브 웹 서버.

- 기존 메인화면(싸이월드 클래식 레이아웃)을 그대로 재현: 상단 TODAY/TOTAL,
  좌측 프로필(미니미·대표사진·도토리·일촌·CYWORLD), 중앙 Updated news/Mini Room/방명록,
  우측 세로탭. 각 메뉴/탭을 클릭하면 해당 기능으로 이동·이용한다.
- 시점 전환(주인/일촌/방문자): viewer에 따라 공개범위가 화면에 그대로 적용된다.
  (도토리·비밀글·나만보기 사진/일기·쪽지함이 방문자에게는 가려진다)
- stdlib http.server 기반(의존성 0). 상태는 인메모리(재시작 시 시드 초기화).

실행:  python serve.py  →  http://127.0.0.1:8000
"""
import base64
import html
import os
import re
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, ROOT)
STATIC = os.path.join(ROOT, "static")

from server.contexts.acorn.acorn import AcornService
from server.contexts.bgm.bgm import BgmService
from server.contexts.bgm import bgm as bgm_mod
from server.contexts.board.board import BoardService
from server.contexts.diary.diary import DiaryService
from server.contexts.favorite.favorite import FavoriteService
from server.contexts.guestbook.guestbook import GuestbookService
from server.contexts.ilchon.ilchon import IlchonService
from server.contexts.message.message import MessageService
from server.contexts.minihome.minihome import MinihomeService
from server.contexts.photo.photo import PhotoService
from server.contexts.shop.shop import ShopService
from server.contexts.shop import shop as shop_mod

OWNER = "과니"

# 시점 전환: (viewer_id, 라벨). 병익=일촌, 지나가던손님=비일촌 방문자
VIEWS = [(OWNER, "주인(본인)"), ("병익", "일촌"), ("지나가던손님", "방문자")]
_view = {"who": OWNER}  # 현재 보는 시점
_miniroom = {"uri": ""}  # 업로드한 미니룸 이미지(data URI). 비면 고정 파일/기본 SVG

# 미니룸 벽지: 이름 → (배경, 좌벽, 우벽) 색
WALLPAPERS = {
    "하늘": ("#d7ecf7", "#cfe3f3", "#bcd6ec"),
    "핑크": ("#fbe0ec", "#f7cfe0", "#f0bcd4"),
    "민트": ("#dcf2e8", "#cfe9dd", "#bce0cf"),
    "레몬": ("#fbf3d2", "#f5ecc2", "#ece0a8"),
    "라일락": ("#ece2f5", "#e0d2ef", "#d2bce8"),
    "그레이": ("#e8eef2", "#dde5ec", "#cfd9e2"),
}
_wallpaper = {"name": "하늘"}


def _static_miniroom():
    """static/miniroom.* 고정 파일이 있으면 그 URL 경로를 반환."""
    for ext in ("png", "jpg", "jpeg", "gif", "webp"):
        if os.path.exists(os.path.join(STATIC, f"miniroom.{ext}")):
            return f"/static/miniroom.{ext}"
    return ""


_UP_EXTS = ("png", "jpg", "gif", "webp")


def _find_uploaded():
    """영속화된 업로드 미니룸(static/miniroom_uploaded.*)의 URL을 반환."""
    for ext in _UP_EXTS:
        if os.path.exists(os.path.join(STATIC, f"miniroom_uploaded.{ext}")):
            return f"/static/miniroom_uploaded.{ext}"
    return ""


def _clear_uploaded():
    for ext in _UP_EXTS:
        try:
            os.remove(os.path.join(STATIC, f"miniroom_uploaded.{ext}"))
        except OSError:
            pass


def _save_uploaded(data_uri):
    """data URI를 디코딩해 static/miniroom_uploaded.<ext>로 영속 저장. 성공 시 URL 반환."""
    m = re.match(r"data:image/([\w]+);base64,(.+)$", data_uri, re.S)
    if not m:
        return ""
    ext = {"jpeg": "jpg"}.get(m.group(1).lower(), m.group(1).lower())
    if ext not in _UP_EXTS:
        ext = "png"
    try:
        raw = base64.b64decode(m.group(2))
        _clear_uploaded()
        os.makedirs(STATIC, exist_ok=True)
        with open(os.path.join(STATIC, f"miniroom_uploaded.{ext}"), "wb") as fh:
            fh.write(raw)
        return f"/static/miniroom_uploaded.{ext}"
    except (ValueError, OSError):
        return ""

# --- 서버 생애 동안 유지되는 도메인 상태 ---
_seq = {"t": 0.0}


def _clock():
    _seq["t"] += 1
    return _seq["t"]


ilchon = IlchonService()
acorn = AcornService(ilchon=ilchon)
blocks = {}
guestbook = GuestbookService(blocks=blocks, clock=_clock)
photo = PhotoService(ilchon=ilchon, clock=_clock)
gallery = PhotoService(ilchon=ilchon, clock=_clock)  # 갤러리 = 사진첩 모델 재사용(별도 인스턴스)
diary = DiaryService(ilchon=ilchon, clock=_clock)
message = MessageService(blocks=blocks, clock=_clock)
board = BoardService(blocks=blocks, clock=_clock)
favorite = FavoriteService()
bgm = BgmService()
shop = ShopService()
home = MinihomeService(ilchon=ilchon, acorn=acorn, guestbook=guestbook,
                       photo=photo, diary=diary, message=message, board=board)


def _seed():
    for f, a, b in [("병익", "베프", "단짝"), ("효정", "동네친구", "동네친구"),
                    ("계희", "회사동기", "회사동기")]:
        ilchon.request(OWNER, f, a, b)
        ilchon.accept(OWNER, f)
    # 파도타기용: 일촌의 일촌(friend-of-friend) — 과니의 직접 일촌 아님
    for a, b in [("병익", "수민"), ("병익", "지호"), ("효정", "하늘"), ("계희", "도윤")]:
        ilchon.request(a, b, "친구", "친구")
        ilchon.accept(a, b)
    acorn.charge(OWNER, 1500, entry_id="seed-charge")
    acorn.purchase(OWNER, 300, entry_id="seed-buy", ref="미니룸 벽지")
    photo.upload(OWNER, OWNER, "제주도 바다", scope="public")
    photo.upload(OWNER, OWNER, "일촌 모임", scope="ilchon")
    photo.upload(OWNER, OWNER, "셀카 (나만보기)", scope="private")
    photo.set_cover(OWNER, photo.list_for(OWNER, OWNER)[0].photo_id, OWNER)
    gallery.upload(OWNER, OWNER, "여행 스케치", scope="public")
    gallery.upload(OWNER, OWNER, "일촌 단체샷", scope="ilchon")
    diary.write(OWNER, OWNER, "첫 일기", "미니홈피 시작!", mood="😊", scope="public")
    diary.write(OWNER, OWNER, "일촌만 보는 글", "우리끼리 얘기", mood="🤫", scope="ilchon")
    diary.write(OWNER, OWNER, "혼자 쓰는 글", "비밀일기", mood="😴", scope="private")
    home.set_private(OWNER, {"diary"})  # 다이어리 섹션 비공개(일촌·본인만)
    guestbook.post(OWNER, "병익", "오랜만에 미니홈피 왔다 간다~ 일촌평 남겨줘!")
    guestbook.post(OWNER, "효정", "BGM 뭐야? 노래 좋다 ♪")
    guestbook.post(OWNER, "계희", "우리끼리 비밀 얘기...", secret=True)
    board.write(OWNER, "병익", "첫 방문 인사", "미니홈피 잘 봤어요~ 일촌해요!")
    board.write(OWNER, OWNER, "공지: 방명록 자유롭게", "놀러오면 흔적 남겨주세요 :)")
    message.send("병익", OWNER, "오늘 미니홈피 놀러왔어!")
    message.send("효정", OWNER, "BGM 추천 좀~")
    for t in ["병익", "효정", "수민"]:
        favorite.add(OWNER, t)
    # 도토리 소비처 시드: BGM 1곡 + 아이템 2개 구매
    bgm.buy(acorn, OWNER, "spring")
    shop.buy(acorn, OWNER, "plant")
    shop.buy(acorn, OWNER, "clock")
    for v in ["병익", "효정", "계희", "지나가던손님", "병익"]:
        home.open(OWNER, v)


_seed()
# 재접속/재시작에도 유지: 영속화된 업로드 미니룸 복원
_miniroom["uri"] = _find_uploaded()


# ---------- 렌더 헬퍼 ----------
def esc(s):
    return html.escape(str(s))


def viewer():
    return _view["who"]


def is_owner():
    return viewer() == OWNER


# 우측 세로탭 (이미지 순서). gallery/fav는 deferred placeholder.
TABS = [("profile", "프로필"), ("diary", "다이어리"), ("photo", "사진첩"),
        ("gallery", "갤러리"), ("board", "게시판"), ("guestbook", "방명록"),
        ("bgm", "BGM"), ("shop", "아이템샵"), ("fav", "즐겨찾기")]


def scope_select(name="scope"):
    return (f'<select name="{name}">'
            '<option value="public">전체공개</option>'
            '<option value="ilchon">일촌공개</option>'
            '<option value="private">나만보기</option>'
            '</select>')


def scope_badge(scope):
    label = {"public": "전체", "ilchon": "일촌", "private": "나만"}.get(scope, scope)
    return f'<span class="badge s-{scope}">{label}</span>'


def view_switch(active_tab):
    btns = []
    for who, label in VIEWS:
        on = "on" if who == viewer() else ""
        btns.append(f'<a class="vbtn {on}" href="/switch?who={urllib.parse.quote(who)}&tab={active_tab}">{esc(label)}</a>')
    return '<span class="vlabel">👁 시점</span>' + "".join(btns)


def shell(active, center):
    p = home.main(OWNER, viewer())
    tabs = "\n".join(
        f'<a href="/?tab={t}" class="vtab {"on" if t == active else ""}">{esc(label)}</a>'
        for t, label in TABS)
    acorn_html = (f'<div class="pf-acorn">🌰 도토리 <b>{p["acorn_balance"]}</b></div>'
                  if "acorn_balance" in p else
                  '<div class="pf-acorn off">🌰 도토리 <b>비공개</b></div>')
    cover = p.get("photo_cover")
    cover_html = (f'<div class="pf-cover">📷 대표사진<br><b>{esc(cover) if cover else "없음"}</b>'
                  f'<span class="pf-cnt">사진첩 {p.get("photo_count",0)}장</span></div>')
    return f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{esc(OWNER)}님의 미니홈피</title>
<style>
  * {{ box-sizing:border-box; }}
  body {{ margin:0; padding:8px; background:#6f9fc8;
         font-family:"맑은 고딕","Malgun Gothic",Dotum,sans-serif; font-size:12px; color:#333; }}
  a {{ color:#2c5f86; }}
  .cy {{ width:880px; margin:0 auto; background:#fff; border:1px solid #356; border-radius:4px;
        box-shadow:0 8px 30px rgba(0,0,0,.3); overflow:hidden; }}
  .cy-top {{ display:flex; align-items:center; gap:14px; padding:7px 12px;
            background:linear-gradient(#fafdff,#dcebf7); border-bottom:1px solid #9cc3df; }}
  .counter b {{ font-size:13px; }} .t-today {{ color:#d23; }} .t-total {{ color:#558; }}
  .cy-title {{ flex:1; text-align:center; font-size:15px; font-weight:bold; color:#2c5f86; letter-spacing:1px; }}
  .cy-url {{ font-size:11px; color:#789; }}
  .switch {{ display:flex; align-items:center; gap:5px; padding:5px 12px; background:#eaf3fb;
            border-bottom:1px solid #cfe0ee; font-size:11px; }}
  .vlabel {{ color:#789; margin-right:4px; }}
  .vbtn {{ text-decoration:none; padding:3px 10px; border:1px solid #a9c8e0; border-radius:12px;
          background:#fff; color:#2c5f86; }}
  .vbtn.on {{ background:#2c5f86; color:#fff; border-color:#234; font-weight:bold; }}
  .cy-body {{ display:flex; }}
  .col-left {{ width:172px; background:#eef5fb; border-right:1px solid #cfe0ee; padding:12px; }}
  .today-is {{ font-size:11px; color:#d23; margin-bottom:6px; }} .today-is b {{ color:#333; }}
  .avatar {{ height:124px; border:1px solid #e6b9cd; border-radius:5px; position:relative; overflow:hidden;
            background:linear-gradient(#cfefff,#bfe6ff 55%,#a9d49a 55%,#9ccb8d); }}
  .avatar .doll {{ position:absolute; left:50%; bottom:8px; transform:translateX(-50%); width:54px; height:84px;
                  background:#ffd23f; border-radius:26px 26px 12px 12px; box-shadow:inset -5px -5px rgba(0,0,0,.08); }}
  .avatar .doll::before {{ content:""; position:absolute; top:13px; left:15px; width:7px; height:7px;
                          background:#333; border-radius:50%; box-shadow:16px 0 #333; }}
  .avatar .sun {{ position:absolute; top:8px; right:10px; font-size:18px; }}
  .pf-title {{ margin-top:10px; font-weight:bold; color:#2c5f86; text-align:center; }}
  .pf-sub {{ text-align:center; color:#888; font-size:11px; }}
  .pf-acts {{ margin-top:8px; text-align:center; font-size:11px; }} .pf-acts a {{ color:#789; text-decoration:none; }}
  .pf-cover {{ margin-top:12px; background:#f2f8ff; border:1px solid #cfe0ee; border-radius:5px;
              padding:6px; text-align:center; font-size:11px; color:#557; }}
  .pf-cover b {{ display:block; color:#2c5f86; margin:2px 0; }} .pf-cnt {{ color:#9ab; display:block; }}
  .pf-acorn {{ margin-top:10px; background:#fff6e2; border:1px solid #f0d59a; border-radius:5px; padding:6px; text-align:center; }}
  .pf-acorn b {{ color:#c87f10; }} .pf-acorn.off {{ background:#f0f0f0; border-color:#ddd; }} .pf-acorn.off b {{ color:#999; }}
  .pf-ilchon {{ margin-top:8px; text-align:center; }} .pf-ilchon a {{ color:#2c5f86; text-decoration:none; }}
  .pf-logo {{ margin-top:12px; text-align:center; font-weight:bold; color:#2c5f86; }}
  .pf-mail {{ text-align:center; color:#9ab; font-size:11px; }}
  .col-mid {{ flex:1; padding:10px 14px; }}
  .col-right {{ width:78px; background:#dcebf7; border-left:1px solid #b6d3e8; padding-top:8px; }}
  .vtab {{ display:block; margin:4px 7px; padding:8px 0; text-align:center; text-decoration:none;
          background:linear-gradient(#fbfdff,#cfe2f2); border:1px solid #a9c8e0; border-radius:3px;
          color:#2c5f86; font-size:11px; }}
  .vtab.on {{ background:#2c5f86; color:#fff; border-color:#234; font-weight:bold; }}
  .bar {{ background:linear-gradient(#eaf4fc,#d4e8f7); border:1px solid #b6d3e8; border-radius:3px;
         padding:4px 9px; font-weight:bold; color:#2c5f86; }} .bar small {{ color:#9ab; font-weight:normal; margin-left:6px; }}
  .menu-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:3px 20px; margin:10px 4px; }}
  .menu-grid a {{ display:flex; justify-content:space-between; padding:3px 4px; text-decoration:none;
                 color:#2c5f86; border-bottom:1px dotted #d6e3ee; }}
  .menu-grid a.off {{ color:#aab; }} .menu-grid .cnt {{ color:#d23; }} .menu-grid a.off .cnt {{ color:#bbc; }}
  .miniroom-bar {{ margin-top:14px; display:flex; justify-content:space-between; align-items:center; }}
  .mr-r {{ color:#c87f10; font-size:11px; }}
  .miniroom {{ margin-top:6px; border:1px solid #b8d4e6; border-radius:4px; position:relative;
              background:#d7ecf7; overflow:hidden; text-align:center; }}
  .miniroom .mr-svg {{ display:inline-block; height:270px; width:auto; max-width:100%; vertical-align:top; }}
  .miniroom .mr-img {{ display:block; width:100%; max-height:300px; object-fit:contain; image-rendering:pixelated; }}
  .mr-up {{ margin-top:6px; display:flex; gap:7px; align-items:center; flex-wrap:wrap;
           background:#fdf0f5; border:1px solid #f0cdde; border-radius:5px; padding:8px; }}
  .wp-bar {{ display:flex; align-items:center; gap:6px; margin:6px 0; }}
  .wp-l {{ font-size:11px; color:#789; margin-right:2px; }}
  .wp {{ width:20px; height:20px; border-radius:50%; border:2px solid #fff; box-shadow:0 0 0 1px #bcd;
        display:inline-block; cursor:pointer; }}
  .wp.on {{ box-shadow:0 0 0 2px #2c5f86; }}
  .miniroom .tag {{ position:absolute; top:6px; right:8px; z-index:2; background:#fff; border:1px solid #cdb; border-radius:3px; padding:1px 6px; color:#c87f10; }}
  .room-acts {{ margin-top:6px; text-align:center; font-size:11px; color:#789; }} .room-acts span {{ margin:0 6px; }}
  h2 {{ font-size:14px; color:#c0392b; border-left:4px solid #c0392b; padding-left:8px; margin:10px 0 7px; }}
  .friends h3 {{ font-size:12px; color:#2c5f86; margin:14px 0 6px; }}
  form.box {{ background:#eef5fb; border:1px solid #cfe0ee; border-radius:5px; padding:11px; margin-bottom:14px; }}
  form.box .row {{ display:flex; gap:7px; margin-bottom:7px; align-items:center; flex-wrap:wrap; }}
  input[type=text],input[type=number],textarea,select {{ padding:6px 8px; border:1px solid #bcd; border-radius:4px; font-size:13px; }}
  input.grow {{ flex:1; min-width:120px; }} textarea {{ width:100%; height:54px; resize:vertical; }}
  button.go {{ padding:7px 16px; background:#2c5f86; color:#fff; border:none; border-radius:4px; cursor:pointer; }}
  ul.list {{ list-style:none; margin:0; padding:0; }}
  .item {{ border:1px solid #e3eef6; border-radius:5px; padding:9px 11px; margin-bottom:7px; position:relative; }}
  .item .hd {{ display:flex; justify-content:space-between; align-items:baseline; gap:8px; }}
  .item .ttl {{ color:#2c5f86; font-weight:bold; }} .item .meta {{ color:#9ab; font-size:11px; }}
  .item .bd {{ margin-top:5px; white-space:pre-wrap; }}
  .gb-item {{ border-bottom:1px dashed #dde6ee; padding:7px 2px; display:flex; gap:9px; }}
  .gb-author {{ min-width:54px; color:#2c5f86; font-weight:bold; }}
  .act {{ position:absolute; top:7px; right:9px; display:flex; gap:4px; }} .act form {{ margin:0; }}
  .act button {{ background:#fff; border:1px solid #cdd; color:#789; border-radius:4px; padding:2px 7px; font-size:11px; cursor:pointer; }}
  .act button.del {{ border-color:#e0b4b4; color:#c0392b; }}
  .badge {{ font-size:10px; border-radius:3px; padding:1px 5px; color:#fff; }}
  .s-public {{ background:#3a8; }} .s-ilchon {{ background:#37a; }} .s-private {{ background:#a47; }}
  .lock {{ color:#999; font-style:italic; }} .secret {{ background:#c0392b; color:#fff; border-radius:3px; padding:0 5px; font-size:10px; }}
  .empty {{ color:#999; padding:14px; text-align:center; }}
  .notice {{ background:#fff8e6; border:1px solid #f0d59a; border-radius:5px; padding:10px; color:#a87; }}
  .grid {{ display:grid; grid-template-columns:1fr 1fr; gap:8px; }}
  .ph {{ border:1px solid #e3eef6; border-radius:5px; padding:9px; text-align:center; position:relative; }}
  .ph .thumb {{ height:72px; background:repeating-linear-gradient(45deg,#eef,#eef 8px,#dde 8px,#dde 16px);
               border-radius:4px; display:flex; align-items:center; justify-content:center; font-size:24px; overflow:hidden; }}
  .ph .thumb img {{ max-height:72px; max-width:100%; object-fit:cover; }}
  .ph.cover {{ border:2px solid #f0a; }} .ph .cap {{ margin-top:5px; font-size:12px; }}
  .dimg {{ max-width:220px; max-height:150px; border-radius:5px; margin-top:6px; border:1px solid #cde; display:block; }}
  .hint {{ font-size:11px; color:#9ab; }}
  .foot {{ text-align:center; font-size:11px; color:#9bb; padding:9px; border-top:1px solid #e3eef6; }}
</style></head>
<body>
  <div class="cy">
    <div class="cy-top">
      <span class="counter"><span class="t-today">TODAY <b>{p['today']}</b></span>
        &nbsp;|&nbsp; <span class="t-total">TOTAL <b>{p['total']}</b></span></span>
      <span class="cy-title">사이좋은 사람들</span>
      <span class="cy-url">http://www.cyworld.com/{esc(OWNER)}</span>
    </div>
    <div class="switch">{view_switch(active)}
      <span style="margin-left:auto;color:#9ab">현재 보는 사람: <b>{esc(viewer())}</b></span></div>
    <div class="cy-body">
      <aside class="col-left">
        <div class="today-is">TODAY IS... <b>행복</b></div>
        <a href="/?tab=home"><div class="avatar"><span class="sun">☀️</span><div class="doll"></div></div></a>
        <div class="pf-title">{esc(OWNER)}</div>
        <div class="pf-sub">사이좋은 사람들 · 싸이월드</div>
        <div class="pf-acts"><a href="/?tab=profile">✎ EDIT</a> | <a href="/?tab=home">⟳ HISTORY</a></div>
        {cover_html}
        {acorn_html}
        <div class="pf-ilchon"><a href="/?tab=ilchon">👥 일촌 <b>{p['ilchon_count']}</b>명</a></div>
        <div class="pf-logo">CYWORLD ②</div>
        <div class="pf-mail">{esc(OWNER)}@cyworld.com</div>
      </aside>
      <main class="col-mid">
{center}
      </main>
      <nav class="col-right">
{tabs}
      </nav>
    </div>
  </div>
<script>
function readImg(input){{
  var f = input.files[0]; if(!f) return;
  if(f.size > 600000){{ alert('600KB 이하 이미지만 올려주세요'); input.value=''; return; }}
  var r = new FileReader();
  r.onload = function(e){{ input.form.querySelector('input[name=image_uri]').value = e.target.result; }};
  r.readAsDataURL(f);
}}
// --- BGM: Web Audio API 멜로디 합성 (음원 파일 0) ---
var BGM_NOTES = {{ spring:[523,659,784,880,784,659], night:[440,392,330,294,330,392], rain:[330,294,262,294,330,392] }};
var _actx=null, _bgmTimer=null;
function stopBgm(){{ if(_bgmTimer){{ clearTimeout(_bgmTimer); _bgmTimer=null; }} }}
function playBgm(id){{
  stopBgm();
  var notes = BGM_NOTES[id]; if(!notes) return;
  if(!_actx) _actx = new (window.AudioContext||window.webkitAudioContext)();
  if(_actx.state==='suspended') _actx.resume();  // 사용자 제스처에서 호출
  function loop(){{
    var t0 = _actx.currentTime;
    notes.forEach(function(f,i){{
      var o=_actx.createOscillator(), g=_actx.createGain();
      o.type='sine'; o.frequency.value=f; o.connect(g); g.connect(_actx.destination);
      var st=t0+i*0.36;
      g.gain.setValueAtTime(0.0001, st);
      g.gain.exponentialRampToValueAtTime(0.18, st+0.02);
      g.gain.exponentialRampToValueAtTime(0.0001, st+0.33);
      o.start(st); o.stop(st+0.35);
    }});
    _bgmTimer = setTimeout(loop, notes.length*360 + 250);
  }}
  loop();
}}
</script>
</body></html>"""


# ---------- 미니룸 (아이소메트릭 3D 픽셀아트 SVG) ----------
_TW, _TH, _OX, _OY = 34, 17, 300, 36


def _iso(x, y, z=0):
    """그리드 좌표(x,y)+높이 z → 화면 좌표 (2:1 아이소메트릭)."""
    return f"{_OX + (x - y) * _TW:.0f},{_OY + (x + y) * _TH - z:.0f}"


def _box(x0, y0, dx, dy, zb, h, ct, cr, cf):
    """아이소 직육면체(가구): top/right/front 3면을 명암으로."""
    zt = zb + h
    top = f"{_iso(x0,y0,zt)} {_iso(x0+dx,y0,zt)} {_iso(x0+dx,y0+dy,zt)} {_iso(x0,y0+dy,zt)}"
    right = f"{_iso(x0+dx,y0,zt)} {_iso(x0+dx,y0+dy,zt)} {_iso(x0+dx,y0+dy,zb)} {_iso(x0+dx,y0,zb)}"
    front = f"{_iso(x0,y0+dy,zt)} {_iso(x0+dx,y0+dy,zt)} {_iso(x0+dx,y0+dy,zb)} {_iso(x0,y0+dy,zb)}"
    return (f'<polygon points="{top}" fill="{ct}"/>'
            f'<polygon points="{right}" fill="{cr}"/>'
            f'<polygon points="{front}" fill="{cf}"/>')


def render_miniroom():
    bg, lwc, rwc = WALLPAPERS.get(_wallpaper["name"], WALLPAPERS["하늘"])
    G = 6
    WH = 96  # 벽 높이
    s = []
    # 바닥
    floor = f"{_iso(0,0)} {_iso(G,0)} {_iso(G,G)} {_iso(0,G)}"
    s.append(f'<polygon points="{floor}" fill="#e7f0e6"/>')
    # 바닥 격자선
    for i in range(1, G):
        s.append(f'<line x1="{_iso(i,0).split(",")[0]}" y1="{_iso(i,0).split(",")[1]}" x2="{_iso(i,G).split(",")[0]}" y2="{_iso(i,G).split(",")[1]}" stroke="#d2e2d0" stroke-width="1"/>')
        s.append(f'<line x1="{_iso(0,i).split(",")[0]}" y1="{_iso(0,i).split(",")[1]}" x2="{_iso(G,i).split(",")[0]}" y2="{_iso(G,i).split(",")[1]}" stroke="#d2e2d0" stroke-width="1"/>')
    # 좌벽(x=0 면)·우벽(y=0 면)
    lwall = f"{_iso(0,0,0)} {_iso(0,G,0)} {_iso(0,G,WH)} {_iso(0,0,WH)}"
    rwall = f"{_iso(0,0,0)} {_iso(G,0,0)} {_iso(G,0,WH)} {_iso(0,0,WH)}"
    s.append(f'<polygon points="{lwall}" fill="{lwc}"/>')
    s.append(f'<polygon points="{rwall}" fill="{rwc}"/>')
    # 창문 (아치형): 우벽 2개 + 좌벽 1개

    def window(face, a, b, z0, z1):
        # face: 'r'(y=0) → x:a..b, 'l'(x=0) → y:a..b
        if face == 'r':
            pts = f"{_iso(a,0,z1)} {_iso(b,0,z1)} {_iso(b,0,z0)} {_iso(a,0,z0)}"
            cap = f"{_iso(a,0,z1)} {_iso((a+b)/2,0,z1+12)} {_iso(b,0,z1)}"
        else:
            pts = f"{_iso(0,a,z1)} {_iso(0,b,z1)} {_iso(0,b,z0)} {_iso(0,a,z0)}"
            cap = f"{_iso(0,a,z1)} {_iso(0,(a+b)/2,z1+12)} {_iso(0,b,z1)}"
        return (f'<polygon points="{pts}" fill="#dff1ff" stroke="#fff" stroke-width="3"/>'
                f'<polygon points="{cap}" fill="#dff1ff" stroke="#fff" stroke-width="3"/>')
    s.append(window('r', 1.2, 2.4, 40, 78))
    s.append(window('r', 3.4, 4.6, 40, 78))
    s.append(window('l', 1.4, 3.0, 42, 76))
    # 러그(바닥 중앙)
    rug = f"{_iso(2,2)} {_iso(4.5,2)} {_iso(4.5,4.5)} {_iso(2,4.5)}"
    s.append(f'<polygon points="{rug}" fill="#f3b9c8" opacity="0.55"/>')
    # --- 가구 (뒤→앞 순서로 그려 겹침 정상) ---
    # 좌측 책장(뒤)
    s.append(_box(0.2, 0.4, 0.5, 1.6, 0, 64, "#e3cba0", "#caa86f", "#b89357"))
    # 화분 + 식물
    s.append(_box(0.3, 2.4, 0.5, 0.5, 0, 14, "#d98b4a", "#c2773a", "#a9652f"))
    s.append(f'<circle cx="{_iso(0.55,2.65,28).split(",")[0]}" cy="{_iso(0.55,2.65,28).split(",")[1]}" r="13" fill="#5aa84a"/>')
    s.append(f'<circle cx="{_iso(0.55,2.65,40).split(",")[0]}" cy="{_iso(0.55,2.65,40).split(",")[1]}" r="9" fill="#6cbf57"/>')
    # 책상 + 모니터(중앙 좌)
    s.append(_box(1.1, 0.3, 1.3, 0.7, 0, 30, "#e6c79a", "#cba972", "#b8965c"))
    s.append(_box(1.5, 0.45, 0.5, 0.35, 30, 22, "#3a4250", "#2c333f", "#222831"))
    s.append(f'<polygon points="{_iso(1.55,0.5,34)} {_iso(1.95,0.5,34)} {_iso(1.95,0.5,48)} {_iso(1.55,0.5,48)}" fill="#7fd0ff"/>')
    # 침대(우측): 프레임 + 매트 + 이불 + 베개
    s.append(_box(3.3, 0.4, 2.3, 1.7, 0, 16, "#c79b76", "#ad825f", "#94704f"))
    s.append(_box(3.3, 0.4, 2.3, 1.7, 16, 10, "#fbfdff", "#e7edf3", "#dbe3ea"))
    s.append(_box(3.3, 0.4, 1.5, 1.7, 26, 6, "#f6c0d2", "#e7a3bb", "#d98fa9"))  # 이불
    s.append(_box(5.0, 0.5, 0.55, 0.7, 26, 9, "#ffffff", "#eef2f6", "#e2e8ef"))  # 베개
    # 거울(우측 앞)
    s.append(_box(5.5, 3.6, 0.25, 1.1, 0, 70, "#cfe6f2", "#b6d2e2", "#9fc0d2"))
    # 협탁 + 스탠드
    s.append(_box(2.7, 0.4, 0.6, 0.6, 0, 20, "#e6c79a", "#cba972", "#b8965c"))
    # 아이템샵 보유 가구 배치 (SVG 기본방일 때만 호출됨)
    SHOP_SLOTS = [(4.8, 3.4), (0.7, 4.4), (4.4, 4.8), (1.0, 0.6), (5.2, 1.6), (2.4, 0.5)]
    for i, item_id in enumerate(shop.owned()[:len(SHOP_SLOTS)]):
        _n, emoji, _p = shop_mod.CATALOG[item_id]
        gx, gy = SHOP_SLOTS[i]
        cx, cy = _iso(gx, gy, 0).split(",")
        s.append(f'<text x="{cx}" y="{cy}" font-size="26" text-anchor="middle">{emoji}</text>')
    # --- 미니미 캐릭터(가운데, 주황 옷) ---
    bx, by = 3.0, 3.4
    foot = _iso(bx, by, 0)
    s.append(f'<ellipse cx="{foot.split(",")[0]}" cy="{foot.split(",")[1]}" rx="16" ry="7" fill="#000" opacity="0.12"/>')
    s.append(f'<polygon points="{_iso(bx,by,2)} {_iso(bx+0.18,by,2)} {_iso(bx+0.18,by,30)} {_iso(bx,by,30)}" fill="#e8743b"/>')
    hx, hy = _iso(bx + 0.09, by, 46).split(",")
    s.append(f'<circle cx="{hx}" cy="{hy}" r="11" fill="#ffd9a0" stroke="#e3b277" stroke-width="1.5"/>')
    s.append(f'<path d="M{float(hx)-11},{float(hy)-2} a11,11 0 0 1 22,0 z" fill="#5a3a23"/>')
    s.append(f'<circle cx="{float(hx)-4}" cy="{float(hy)+1}" r="1.6" fill="#333"/><circle cx="{float(hx)+4}" cy="{float(hy)+1}" r="1.6" fill="#333"/>')
    # viewBox를 방 콘텐츠 바운딩 박스(x 96~504, y -60~240)에 타이트하게 맞춰 프레임에 꽉 차게
    return ('<svg viewBox="90 -64 420 312" class="mr-svg" preserveAspectRatio="xMidYMid meet">'
            f'<rect x="90" y="-64" width="420" height="312" fill="{bg}"/>'
            + "".join(s) + '</svg>')


# ---------- 탭별 컨텐츠 ----------
def render_home():
    p = home.main(OWNER, viewer())
    rows = []
    for v in reversed(p["recent_guestbook"]):
        body = '<span class="lock">🔒 비밀글입니다</span>' if v.locked else esc(v.content)
        if v.secret and not v.locked:
            body = f'<span class="secret">비밀</span> {body}'
        rows.append(f'<li class="gb-item"><b class="gb-author">{esc(v.author_id)}</b><span>{body}</span></li>')
    gb_html = "\n".join(rows) or '<li class="empty">방명록이 없어요.</li>'

    diary_lock = "🔒" if "diary" in p.get("sections", []) else ""
    msg = (f'{p["message_unread"]}/{p["message_total"]}' if "message_unread" in p else "비공개")
    return f"""<div class="bar">Updated news <small>TODAY STORY</small></div>
<div class="menu-grid">
  <a href="/?tab=diary">다이어리 {diary_lock} <span class="cnt">{p.get('diary_count',0)}</span></a>
  <a href="/?tab=message">쪽지함 <span class="cnt">{msg}</span></a>
  <a href="/?tab=photo">사진첩 <span class="cnt">{p.get('photo_count',0)}</span></a>
  <a href="/?tab=gallery">갤러리 <span class="cnt">{gallery.count_visible(OWNER, viewer())}</span></a>
  <a href="/?tab=board">게시판 <span class="cnt">{p.get('board_count',0)}/99</span></a>
  <a href="/?tab=ilchon" class="off">친구찾기 <span class="cnt">{p['ilchon_count']}</span></a>
</div>
<div class="miniroom-bar"><div class="bar" style="flex:1">Mini Room <small>EXPRESS YOURSELF</small></div><div class="mr-r">와플준비중</div></div>
{_wallpaper_picker()}
<div class="miniroom" style="background:{WALLPAPERS.get(_wallpaper['name'], WALLPAPERS['하늘'])[0]}"><span class="tag">미니룸 벽지: {esc(_wallpaper['name'])}</span>{_miniroom_inner()}</div>
{_miniroom_upload()}
<div class="room-acts"><span>◀ 미니룸 ▶</span><span>DIY 룸수리</span><span>일촌사진트리</span><span>미니미 달showroom</span></div>
<section class="friends"><h3>What friends say <small>방명록</small></h3><ul class="list">{gb_html}</ul></section>"""


def _miniroom_inner():
    # 우선순위: 업로드 이미지 > static 고정 파일 > 기본 SVG(벽지 적용)
    if _miniroom["uri"]:
        return f'<img class="mr-img" src="{_miniroom["uri"]}" alt="미니룸"/>'
    static_url = _static_miniroom()
    if static_url:
        return f'<img class="mr-img" src="{static_url}" alt="미니룸"/>'
    return render_miniroom()


def _wallpaper_picker():
    if not is_owner():
        return ""
    sw = []
    for name, (bg, lw, rw) in WALLPAPERS.items():
        on = "on" if name == _wallpaper["name"] else ""
        sw.append(f'<a class="wp {on}" href="/wallpaper?w={urllib.parse.quote(name)}&tab=home" '
                  f'style="background:{lw}" title="{esc(name)}"></a>')
    return f'<div class="wp-bar"><span class="wp-l">🎨 벽지 꾸미기</span>{"".join(sw)}</div>'


def _miniroom_upload():
    if not is_owner():
        return ""
    has_img = bool(_miniroom["uri"])
    reset = ('<form method="post" action="/miniroom/reset" style="display:inline;margin-left:6px">'
             '<button class="go" style="background:#888">기본 방으로</button></form>'
             if has_img else "")
    note = ("미니룸 이미지를 올리면 교체됩니다 (600KB 이하). 큰 이미지는 static/miniroom.png 로 두면 고정 표시됩니다."
            if not _static_miniroom() else "static/miniroom 파일이 고정 표시 중입니다.")
    return (f'<form class="mr-up" method="post" action="/miniroom/upload">'
            f'<input type="file" accept="image/*" onchange="readImg(this)"/>'
            f'<input type="hidden" name="image_uri"/>'
            f'<button class="go" type="submit">미니룸 이미지로 꾸미기</button>{reset}'
            f'<span class="hint">{note}</span></form>')


def render_profile():
    p = home.main(OWNER, viewer())
    acorn_row = (f'<li class="item"><div class="hd"><span class="ttl">🌰 도토리 잔액</span><span class="meta">{p["acorn_balance"]}개</span></div></li>'
                 if "acorn_balance" in p else
                 '<li class="item"><div class="hd"><span class="ttl">🌰 도토리</span><span class="meta lock">주인만 볼 수 있어요</span></div></li>')
    charge = ("""<h2>도토리 충전</h2>
<form class="box" method="post" action="/acorn/charge">
  <div class="row"><input type="number" name="amount" class="grow" placeholder="충전할 도토리 수" min="1" value="100" required/>
    <button class="go" type="submit">충전</button></div></form>""" if is_owner() else "")
    return f"""<h2>프로필</h2>
<ul class="list">
  <li class="item"><div class="hd"><span class="ttl">미니미</span><span class="meta">{esc(p['minimi_id'])}</span></div></li>
  {acorn_row}
  <li class="item"><div class="hd"><span class="ttl">👥 일촌</span><span class="meta">{p['ilchon_count']}명</span></div></li>
  <li class="item"><div class="hd"><span class="ttl">📷 사진 / 📖 게시판 / 📔 다이어리</span>
    <span class="meta">{p.get('photo_count',0)} / {p.get('board_count',0)} / {p.get('diary_count',0)}</span></div></li>
</ul>
{charge}"""


def render_diary():
    p = home.main(OWNER, viewer())
    if "diary" not in p.get("sections", []):
        return '<h2>다이어리</h2><div class="notice">🔒 비공개 다이어리입니다. 일촌만 볼 수 있어요.</div>'
    items = []
    for d in reversed(diary.list_for(OWNER, viewer())):
        delbtn = (f'<div class="act"><form method="post" action="/diary/delete"><input type="hidden" name="id" value="{d.entry_id}"/><button class="del">삭제</button></form></div>' if is_owner() else "")
        img = f'<img class="dimg" src="{d.image_uri}" alt="{esc(d.title)}"/>' if d.image_uri else ""
        items.append(f"""<li class="item">{delbtn}
          <div class="hd"><span class="ttl">{esc(d.mood)} {esc(d.title)}</span>{scope_badge(d.scope)}</div>
          <div class="bd">{esc(d.body)}</div>{img}</li>""")
    lst = "\n".join(items) or '<li class="empty">보이는 일기가 없어요.</li>'
    form = ("""<h2>다이어리 쓰기</h2>
<form class="box" method="post" action="/diary/write">
  <div class="row"><input type="text" name="title" class="grow" placeholder="제목" required/>
    <input type="text" name="mood" placeholder="기분 😊" style="width:90px"/>""" + scope_select() + """</div>
  <textarea name="body" placeholder="오늘의 이야기" required></textarea>
  <div class="row"><input type="file" accept="image/*" onchange="readImg(this)"/>
    <input type="hidden" name="image_uri"/><span class="hint">사진 첨부 (선택사항, 600KB 이하)</span></div>
  <div class="row"><button class="go" type="submit">등록</button></div></form>""" if is_owner() else "")
    return f"""{form}<h2>다이어리 ({diary.count_visible(OWNER, viewer())})</h2><ul class="list">{lst}</ul>"""


def _thumb(ph):
    if ph.image_uri:
        return f'<div class="thumb"><img src="{ph.image_uri}" alt="{esc(ph.caption)}"/></div>'
    return '<div class="thumb">🖼️</div>'


def render_photolike(svc, base, label):
    """사진첩·갤러리 공통 렌더 (동일 PhotoService 모델)."""
    cards = []
    for ph in svc.list_for(OWNER, viewer()):
        cover_cls = " cover" if ph.is_cover else ""
        owner_acts = ""
        if is_owner():
            cb = "" if ph.is_cover else f'<form method="post" action="/{base}/cover"><input type="hidden" name="id" value="{ph.photo_id}"/><button>대표</button></form>'
            owner_acts = f'<div class="act">{cb}<form method="post" action="/{base}/delete"><input type="hidden" name="id" value="{ph.photo_id}"/><button class="del">삭제</button></form></div>'
        cards.append(f"""<div class="ph{cover_cls}">{_thumb(ph)}
          <div class="cap">{esc(ph.caption)} {scope_badge(ph.scope)}{' ⭐' if ph.is_cover else ''}</div>{owner_acts}</div>""")
    grid = ("<div class='grid'>" + "\n".join(cards) + "</div>") if cards else f'<div class="empty">보이는 {label}가 없어요.</div>'
    form = (f"""<h2>{label} 올리기</h2>
<form class="box" method="post" action="/{base}/upload">
  <div class="row"><input type="text" name="caption" class="grow" placeholder="{label} 설명" required/>{scope_select()}</div>
  <div class="row"><input type="file" accept="image/*" onchange="readImg(this)"/>
    <input type="hidden" name="image_uri"/><span class="hint">이미지 선택 (선택사항, 600KB 이하)</span></div>
  <div class="row"><button class="go" type="submit">업로드</button></div></form>""" if is_owner() else "")
    return f"""{form}<h2>{label} ({svc.count_visible(OWNER, viewer())})</h2>{grid}"""


def render_photo():
    return render_photolike(photo, "photo", "사진첩")


def render_board():
    items = []
    for post in board.list_for(OWNER):
        items.append(f"""<li class="item">
          <div class="act"><form method="post" action="/board/delete"><input type="hidden" name="id" value="{post.post_id}"/><button class="del">삭제</button></form></div>
          <div class="hd"><span class="ttl">{esc(post.title)}</span><span class="meta">by {esc(post.author_id)} · #{post.post_id}</span></div>
          <div class="bd">{esc(post.content)}</div></li>""")
    lst = "\n".join(items) or '<li class="empty">아직 글이 없어요.</li>'
    return f"""<h2>게시판 글쓰기</h2>
<form class="box" method="post" action="/board/write">
  <div class="row"><input type="text" name="author" placeholder="이름" value="{esc(viewer())}" style="width:120px" required/>
    <input type="text" name="title" class="grow" placeholder="제목" required/></div>
  <textarea name="content" placeholder="내용" required></textarea>
  <div class="row"><button class="go" type="submit">등록</button></div></form>
<h2>게시판 (최신순)</h2><ul class="list">{lst}</ul>"""


def render_guestbook():
    items = []
    for v in guestbook.list_for(OWNER, viewer()):
        body = '<span class="lock">🔒 비밀글입니다</span>' if v.locked else esc(v.content)
        sec = '<span class="secret">비밀</span> ' if v.secret else ''
        delbtn = (f'<div class="act"><form method="post" action="/guestbook/delete"><input type="hidden" name="id" value="{v.entry_id}"/><button class="del">삭제</button></form></div>'
                  if viewer() in (OWNER, v.author_id) else "")
        items.append(f"""<li class="item">{delbtn}
          <div class="hd"><span class="ttl">{esc(v.author_id)}</span></div>
          <div class="bd">{sec}{body}</div></li>""")
    lst = "\n".join(items) or '<li class="empty">방명록이 없어요.</li>'
    return f"""<h2>방명록 남기기</h2>
<form class="box" method="post" action="/guestbook/write">
  <div class="row"><input type="text" name="author" placeholder="이름" value="{esc(viewer())}" style="width:120px" required/>
    <label style="font-size:12px;color:#789"><input type="checkbox" name="secret" value="1"/> 비밀글</label></div>
  <textarea name="content" placeholder="한마디 남겨주세요" required></textarea>
  <div class="row"><button class="go" type="submit">등록</button></div></form>
<h2>방명록</h2><ul class="list">{lst}</ul>"""


def render_message():
    send_form = f"""<h2>쪽지 보내기 ({esc(OWNER)}에게)</h2>
<form class="box" method="post" action="/message/send">
  <div class="row"><input type="text" name="sender" placeholder="보내는 사람" value="{esc(viewer())}" style="width:120px" required/>
    <input type="text" name="content" class="grow" placeholder="쪽지 내용" required/>
    <button class="go" type="submit">보내기</button></div></form>"""
    if not is_owner():
        return send_form + '<h2>받은 쪽지함</h2><div class="notice">✉️ 받은 쪽지함은 주인만 볼 수 있어요.</div>'
    items = []
    for m in reversed(message.inbox(OWNER)):
        read_btn = '' if m.read else f'<div class="act"><form method="post" action="/message/read"><input type="hidden" name="id" value="{m.msg_id}"/><button>읽음</button></form></div>'
        flag = '' if m.read else '🔴 '
        items.append(f"""<li class="item">{read_btn}
          <div class="hd"><span class="ttl">{flag}{esc(m.sender_id)}</span><span class="meta">#{m.msg_id}</span></div>
          <div class="bd">{esc(m.content)}</div></li>""")
    lst = "\n".join(items) or '<li class="empty">받은 쪽지가 없어요.</li>'
    return send_form + f'<h2>받은 쪽지함 (안읽음 {message.unread_count(OWNER)}/{len(message.inbox(OWNER))})</h2><ul class="list">{lst}</ul>'


def render_ilchon(waved=""):
    # 파도타기: 일촌의 일촌 중 랜덤 방문 (direct 표면)
    wave_msg = ""
    if waved == "없음":
        wave_msg = '<div class="notice">🌊 파도탈 일촌의 일촌이 없어요.</div>'
    elif waved:
        wave_msg = f'<div class="notice">🌊 <b>{esc(waved)}</b>님의 미니홈피로 파도타기! (일촌의 일촌 랜덤 방문)</div>'
    wave_box = ('<form class="box" method="post" action="/ilchon/wave" style="margin-bottom:8px">'
                '<button class="go" type="submit">🌊 파도타기 — 일촌의 일촌 랜덤 방문</button>'
                '<span class="hint" style="margin-left:8px">내 일촌의 일촌 중 한 명에게로</span></form>')
    items = []
    for f in sorted(ilchon.friends(OWNER)):
        delbtn = (f'<div class="act"><form method="post" action="/ilchon/break"><input type="hidden" name="who" value="{esc(f)}"/><button class="del">파이</button></form></div>' if is_owner() else "")
        items.append(f'<li class="item">{delbtn}<div class="hd"><span class="ttl">👤 {esc(f)}</span></div></li>')
    lst = "\n".join(items) or '<li class="empty">아직 일촌이 없어요.</li>'
    form = ("""<h2>일촌 맺기</h2>
<form class="box" method="post" action="/ilchon/add">
  <div class="row"><input type="text" name="who" class="grow" placeholder="상대 이름" required/>
    <input type="text" name="n1" placeholder="내 호칭" style="width:100px" required/>
    <input type="text" name="n2" placeholder="상대 호칭" style="width:100px" required/>
    <button class="go" type="submit">신청+수락</button></div></form>""" if is_owner() else "")
    return f"""<h2>파도타기</h2>{wave_box}{wave_msg}{form}<h2>내 일촌 ({ilchon.count(OWNER)})</h2><ul class="list">{lst}</ul>"""


def render_gallery():
    return render_photolike(gallery, "gallery", "갤러리")


def render_fav(visited=""):
    # 즐겨찾기는 주인 본인 전용 (FAV AC-5)
    if not is_owner():
        return '<h2>즐겨찾기</h2><div class="notice">⭐ 즐겨찾기는 주인만 볼 수 있어요.</div>'
    visit_msg = (f'<div class="notice">⭐ <b>{esc(visited)}</b>님의 미니홈피로 바로가기!</div>'
                 if visited else "")
    items = []
    for t in favorite.list_for(OWNER):
        items.append(f"""<li class="item">
          <div class="act">
            <form method="post" action="/fav/visit"><input type="hidden" name="who" value="{esc(t)}"/><button>바로가기</button></form>
            <form method="post" action="/fav/remove"><input type="hidden" name="who" value="{esc(t)}"/><button class="del">삭제</button></form></div>
          <div class="hd"><span class="ttl">⭐ {esc(t)}</span><span class="meta">cyworld.com/{esc(t)}</span></div></li>""")
    lst = "\n".join(items) or '<li class="empty">즐겨찾기한 미니홈피가 없어요.</li>'
    return f"""{visit_msg}<h2>즐겨찾기 추가</h2>
<form class="box" method="post" action="/fav/add">
  <div class="row"><input type="text" name="who" class="grow" placeholder="즐겨찾기할 미니홈피 이름" required/>
    <button class="go" type="submit">추가</button></div></form>
<h2>내 즐겨찾기 ({favorite.count(OWNER)})</h2><ul class="list">{lst}</ul>"""


def render_bgm():
    cur = bgm.current()
    cur_title = bgm_mod.CATALOG[cur][0] if cur else "없음"
    player = (f'<div class="notice">🎧 현재 BGM: <b>{esc(cur_title)}</b> &nbsp;'
              f'<button type="button" class="go" onclick="playBgm(\'{cur}\')">▶ 재생</button> '
              f'<button type="button" class="go" style="background:#888" onclick="stopBgm()">⏹ 정지</button></div>'
              if cur else '<div class="notice">현재 설정된 BGM이 없어요. 곡을 구매해 설정하세요.</div>')
    # 보유 곡
    owned = []
    for sid in bgm.owned():
        title, _price = bgm_mod.CATALOG[sid]
        tag = ' <span class="badge s-public">재생중</span>' if sid == cur else ""
        setb = (f'<form method="post" action="/bgm/set"><input type="hidden" name="id" value="{sid}"/><button>현재곡</button></form>'
                if is_owner() and sid != cur else "")
        owned.append(f'<li class="item"><div class="act">'
                     f'<button type="button" onclick="playBgm(\'{sid}\')">▶</button>{setb}</div>'
                     f'<div class="hd"><span class="ttl">🎵 {esc(title)}{tag}</span></div></li>')
    owned_html = "\n".join(owned) or '<li class="empty">보유한 곡이 없어요.</li>'
    # 구매(주인)
    buy = ""
    if is_owner():
        rows = []
        for sid, (title, price) in bgm_mod.CATALOG.items():
            if bgm.owns(sid):
                continue
            rows.append(f'<li class="item"><div class="act"><form method="post" action="/bgm/buy">'
                        f'<input type="hidden" name="id" value="{sid}"/><button>🌰 {price} 구매</button></form></div>'
                        f'<div class="hd"><span class="ttl">🎵 {esc(title)}</span></div></li>')
        cat = "\n".join(rows) or '<li class="empty">모든 곡을 보유했어요.</li>'
        buy = f'<h2>곡 구매 (도토리)</h2><ul class="list">{cat}</ul>'
    return f'<h2>BGM 플레이어</h2>{player}<h2>보유 곡</h2><ul class="list">{owned_html}</ul>{buy}'


def render_shop():
    rows = []
    for item_id in shop.owned():
        name, emoji, _price = shop_mod.CATALOG[item_id]
        rows.append(f'<li class="item"><div class="hd"><span class="ttl">{emoji} {esc(name)}</span></div></li>')
    inv = "\n".join(rows) or '<li class="empty">보유 아이템이 없어요.</li>'
    mode = "기본 SVG 방" if not (_miniroom["uri"] or _static_miniroom()) else "이미지 모드(인벤토리만 표시)"
    note = f'<div class="notice">구매한 가구는 미니룸({mode})에 반영됩니다.</div>'
    buy = ""
    if is_owner():
        crows = []
        for item_id, (name, emoji, price) in shop_mod.CATALOG.items():
            if shop.owns(item_id):
                continue
            crows.append(f'<li class="item"><div class="act"><form method="post" action="/shop/buy">'
                         f'<input type="hidden" name="id" value="{item_id}"/><button>🌰 {price} 구매</button></form></div>'
                         f'<div class="hd"><span class="ttl">{emoji} {esc(name)}</span></div></li>')
        cat = "\n".join(crows) or '<li class="empty">모든 아이템을 보유했어요.</li>'
        buy = f'<h2>아이템샵 (도토리)</h2><ul class="list">{cat}</ul>'
    return f'<h2>내 인벤토리 ({len(shop.owned())})</h2>{note}<ul class="list">{inv}</ul>{buy}'


RENDERERS = {
    "home": render_home, "profile": render_profile, "diary": render_diary,
    "photo": render_photo, "board": render_board, "guestbook": render_guestbook,
    "message": render_message, "ilchon": render_ilchon,
    "gallery": render_gallery, "fav": render_fav,
    "bgm": render_bgm, "shop": render_shop,
}


# ---------- HTTP ----------
class Handler(BaseHTTPRequestHandler):
    def _html(self, body, code=200):
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _redirect(self, tab):
        self.send_response(303)
        self.send_header("Location", f"/?tab={tab}")
        self.end_headers()

    def _form(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode("utf-8")
        return {k: v[0] for k, v in urllib.parse.parse_qs(raw).items()}

    def _serve_static(self, path):
        # /static/<name> 안전 서빙 (디렉터리 탈출 차단)
        name = os.path.basename(path[len("/static/"):])
        fp = os.path.join(STATIC, name)
        if not os.path.isfile(fp):
            return self._html("<h1>404</h1>", code=404)
        mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
                "gif": "image/gif", "webp": "image/webp"}.get(name.rsplit(".", 1)[-1].lower(),
                                                              "application/octet-stream")
        with open(fp, "rb") as fh:
            data = fh.read()
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(parsed.query)
        if parsed.path.startswith("/static/"):
            return self._serve_static(parsed.path)
        if parsed.path == "/wallpaper":
            w = q.get("w", ["하늘"])[0]
            if w in WALLPAPERS:
                _wallpaper["name"] = w
            return self._redirect(q.get("tab", ["home"])[0])
        if parsed.path == "/switch":
            who = q.get("who", [OWNER])[0]
            if who in (w for w, _ in VIEWS):
                _view["who"] = who
            tab = q.get("tab", ["home"])[0]
            return self._redirect(tab if tab in RENDERERS else "home")
        if parsed.path != "/":
            return self._html("<h1>404</h1>", code=404)
        tab = q.get("tab", ["home"])[0]
        if tab == "ilchon":
            center = render_ilchon(q.get("waved", [""])[0])
        elif tab == "fav":
            center = render_fav(q.get("visited", [""])[0])
        else:
            center = RENDERERS.get(tab, render_home)()
        self._html(shell(tab if tab in RENDERERS else "home", center))

    def do_POST(self):
        path = self.path
        f = self._form()
        vw = viewer()
        owner = (vw == OWNER)
        try:
            # 주인 전용 액션 (방문자 차단)
            if path == "/acorn/charge" and owner:
                acorn.charge(OWNER, max(1, int(f.get("amount", "0") or 0)), entry_id=f"web-{_clock()}")
                return self._redirect("profile")
            if path == "/diary/write" and owner:
                diary.write(OWNER, OWNER, f.get("title", "").strip(), f.get("body", "").strip(),
                            mood=f.get("mood", "").strip(), scope=f.get("scope", "public"),
                            image_uri=f.get("image_uri", ""))
                return self._redirect("diary")
            if path == "/diary/delete" and owner:
                diary.delete(OWNER, int(f.get("id", "0")), OWNER)
                return self._redirect("diary")
            # 사진첩·갤러리 공통 (동일 PhotoService 모델)
            m = re.match(r"^/(photo|gallery)/(upload|cover|delete)$", path)
            if m and owner:
                svc = {"photo": photo, "gallery": gallery}[m.group(1)]
                act, tab = m.group(2), m.group(1)
                if act == "upload":
                    svc.upload(OWNER, OWNER, f.get("caption", "").strip(),
                               scope=f.get("scope", "public"), image_uri=f.get("image_uri", ""))
                elif act == "cover":
                    svc.set_cover(OWNER, int(f.get("id", "0")), OWNER)
                else:
                    svc.delete(OWNER, int(f.get("id", "0")), OWNER)
                return self._redirect(tab)
            if path == "/miniroom/upload" and owner:
                saved = _save_uploaded(f.get("image_uri", ""))  # 디코딩 후 파일 영속 저장
                if saved:
                    _miniroom["uri"] = saved  # /static/miniroom_uploaded.<ext>
                return self._redirect("home")
            if path == "/miniroom/reset" and owner:
                _clear_uploaded()  # 영속 파일 삭제 → 재시작에도 기본방
                _miniroom["uri"] = ""
                return self._redirect("home")
            if path == "/ilchon/add" and owner:
                who = f.get("who", "").strip()
                if who:
                    ilchon.request(OWNER, who, f.get("n1", "친구"), f.get("n2", "친구"))
                    ilchon.accept(OWNER, who)
                return self._redirect("ilchon")
            if path == "/ilchon/break" and owner:
                ilchon.break_ilchon(OWNER, f.get("who", "").strip())
                return self._redirect("ilchon")
            if path == "/bgm/buy" and owner:
                bgm.buy(acorn, OWNER, f.get("id", "").strip())
                return self._redirect("bgm")
            if path == "/bgm/set" and owner:
                bgm.set_current(f.get("id", "").strip())
                return self._redirect("bgm")
            if path == "/shop/buy" and owner:
                shop.buy(acorn, OWNER, f.get("id", "").strip())
                return self._redirect("shop")
            if path == "/fav/add" and owner:
                favorite.add(OWNER, f.get("who", "").strip())
                return self._redirect("fav")
            if path == "/fav/remove" and owner:
                favorite.remove(OWNER, f.get("who", "").strip())
                return self._redirect("fav")
            if path == "/fav/visit" and owner:
                # 데모: 실제 미니홈피가 과니뿐 → 파도타기처럼 대상 안내
                dest = f.get("who", "").strip()
                self.send_response(303)
                self.send_header("Location", f"/?tab=fav&visited={urllib.parse.quote(dest)}")
                self.end_headers()
                return
            if path == "/ilchon/wave":
                dest = ilchon.wave(OWNER) or "없음"
                self.send_response(303)
                self.send_header("Location", f"/?tab=ilchon&waved={urllib.parse.quote(dest)}")
                self.end_headers()
                return
            # 방문자도 가능한 액션 (작성 주체 = 현재 시점)
            if path == "/board/write":
                board.write(OWNER, f.get("author", vw).strip() or vw,
                            f.get("title", "").strip(), f.get("content", "").strip())
                return self._redirect("board")
            if path == "/board/delete":
                board.delete(OWNER, int(f.get("id", "0")), vw)
                return self._redirect("board")
            if path == "/guestbook/write":
                guestbook.post(OWNER, f.get("author", vw).strip() or vw,
                               f.get("content", "").strip(), secret=bool(f.get("secret")))
                return self._redirect("guestbook")
            if path == "/guestbook/delete":
                guestbook.delete(int(f.get("id", "0")), vw)
                return self._redirect("guestbook")
            if path == "/message/send":
                message.send(f.get("sender", vw).strip() or vw, OWNER, f.get("content", "").strip())
                return self._redirect("message")
            if path == "/message/read" and owner:
                message.read(int(f.get("id", "0")), OWNER)
                return self._redirect("message")
        except (ValueError, KeyError):
            pass
        # 권한 없음 등 → 해당 탭으로 되돌림
        self._redirect("home")

    def log_message(self, *args):
        pass


def main():
    port = 8000
    if "--port" in sys.argv:
        port = int(sys.argv[sys.argv.index("--port") + 1])
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"[serve] 미니홈피 → http://127.0.0.1:{port}  (Ctrl+C 종료)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n[serve] 종료")


if __name__ == "__main__":
    main()
