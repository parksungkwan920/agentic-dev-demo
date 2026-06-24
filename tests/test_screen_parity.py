# -*- coding: utf-8 -*-
"""UI parity: 미니홈피 메인 렌더가 스냅샷과 일치 (HOME AC-6)."""
import pathlib

from server.contexts.minihome import screens

SNAP = (pathlib.Path(__file__).resolve().parents[1]
        / "sdd/04_verify/10_test/ui_parity/minihome_main.html")


def test_minihome_screen_parity():
    want = SNAP.read_text(encoding="utf-8").strip()
    got = screens.render("minihome_main").strip()
    assert got == want


def test_minihome_screen_essentials():
    html = screens.render("minihome_main")
    # 싸이월드 클래식 핵심 요소
    assert "TODAY" in html and "TOTAL" in html
    assert "Mini Room" in html
    assert "What friends say" in html
    assert "사이좋은 사람들" in html
    assert "방명록" in html  # 우측 세로탭
