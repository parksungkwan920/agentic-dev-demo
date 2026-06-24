# -*- coding: utf-8 -*-
"""pytest 픽스처 + 패키지 경로. 결정적: 고정 rng + 제어 가능한 clock."""
import os
import random
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from server.contexts.acorn.acorn import AcornService  # noqa: E402
from server.contexts.bgm.bgm import BgmService  # noqa: E402
from server.contexts.board.board import BoardService  # noqa: E402
from server.contexts.diary.diary import DiaryService  # noqa: E402
from server.contexts.favorite.favorite import FavoriteService  # noqa: E402
from server.contexts.guestbook.guestbook import GuestbookService  # noqa: E402
from server.contexts.ilchon.ilchon import IlchonService  # noqa: E402
from server.contexts.message.message import MessageService  # noqa: E402
from server.contexts.minihome.minihome import MinihomeService  # noqa: E402
from server.contexts.photo.photo import PhotoService  # noqa: E402
from server.contexts.shop.shop import ShopService  # noqa: E402


@pytest.fixture
def ilchon():
    # seed 고정 rng로 파도타기를 결정적으로
    return IlchonService(rng=random.Random(42))


@pytest.fixture
def acorn(ilchon):
    return AcornService(ilchon=ilchon)


@pytest.fixture
def blocks():
    return {}  # owner_id -> set(blocked author_id)


@pytest.fixture
def guestbook(blocks):
    clock = {"t": 1000.0}
    svc = GuestbookService(blocks=blocks, clock=lambda: clock["t"])
    return svc, clock


@pytest.fixture
def photo(ilchon):
    return PhotoService(ilchon=ilchon, clock=lambda: 0.0)


@pytest.fixture
def diary(ilchon):
    return DiaryService(ilchon=ilchon, clock=lambda: 0.0)


@pytest.fixture
def message(blocks):
    # 차단은 방명록과 동일한 blocks 공유
    return MessageService(blocks=blocks, clock=lambda: 0.0)


@pytest.fixture
def board(blocks):
    # 차단은 방명록과 동일한 blocks 공유
    return BoardService(blocks=blocks, clock=lambda: 0.0)


@pytest.fixture
def favorite():
    return FavoriteService()


@pytest.fixture
def bgm():
    return BgmService()


@pytest.fixture
def shop():
    return ShopService()


@pytest.fixture
def minihome(ilchon, acorn, guestbook, photo, diary, message, board):
    gb, _ = guestbook
    return MinihomeService(ilchon=ilchon, acorn=acorn, guestbook=gb,
                           photo=photo, diary=diary, message=message, board=board)
