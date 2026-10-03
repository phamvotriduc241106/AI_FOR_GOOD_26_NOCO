"""T19: the NOCO Scout entry point and its home page run without errors. No network."""

from __future__ import annotations

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
ENTRY = str(ROOT / "app" / "NOCO_Scout.py")


@pytest.fixture(autouse=True)
def offline(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NOCO_OFFLINE", "1")
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    monkeypatch.syspath_prepend(str(ROOT / "app"))


def _text(app: AppTest) -> str:
    parts = [e.value for e in (*app.title, *app.subheader, *app.markdown, *app.caption)]
    return "\n".join(str(p) for p in parts)


def test_home_page_renders_product_name_cards_and_attribution() -> None:
    app = AppTest.from_file(ENTRY, default_timeout=30).run()
    assert not app.exception
    text = _text(app)
    assert "NOCO Scout" in text
    assert "From an address to a customer-ready quote in seconds." in text
    assert "Address to Quote" in text and "Prospect Map" in text
    assert "How it works" in text
    assert "© OpenStreetMap contributors" in text
    links = app.get("page_link")
    assert len(links) == 2


@pytest.mark.parametrize(
    ("page", "title"),
    [
        ("pages/1_Address_to_Quote.py", "Address to Quote"),
        ("pages/2_Prospect_Map.py", "Prospect Map"),
        ("streamlit_app.py", None),  # the T11 shell titles itself after the chosen feature
    ],
)
def test_every_navigation_page_runs_from_the_entry_point(page: str, title: str | None) -> None:
    app = AppTest.from_file(ENTRY, default_timeout=60).run()
    app.switch_page(page).run()
    assert not app.exception
    if title is None:
        assert any(box.label == "Feature" for box in app.sidebar.selectbox)
    else:
        assert any(title in t.value for t in app.title)
