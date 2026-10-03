"""NOCO Scout: app entry point with a home page and named navigation (task T19).

Run: streamlit run app/NOCO_Scout.py
The pages themselves live in app/pages/ and app/streamlit_app.py; this file only adds the
home page and orders the navigation, so users know where to start.
"""

from __future__ import annotations

import base64
from html import escape
from pathlib import Path

import streamlit as st
from pages.noco_shared import ACCENT, PANEL_BG, apply_style, offline_mode

from features.noco_scout.contract import OSM_ATTRIBUTION

APP_DIR = Path(__file__).resolve().parent
LOGO = APP_DIR.parent / "docs" / "pitch" / "assets" / "noco_logo.png"

address_page = st.Page(
    "pages/1_Address_to_Quote.py",
    title="Address to Quote",
    icon=":material/search:",
    url_path="Address_to_Quote",
)
prospect_page = st.Page(
    "pages/2_Prospect_Map.py",
    title="Prospect Map",
    icon=":material/map:",
    url_path="Prospect_Map",
)

_HOME_CSS = f"""
<style>
.block-container {{ padding-top: 3.6rem !important; max-width: 1180px !important; }}
div[data-testid="stVerticalBlock"] {{ gap: 1.1rem; }}
.noco-hero {{ display: flex; align-items: center; gap: 1.6rem; margin: 0 0 0.4rem; }}
.noco-hero img {{ width: 128px; height: auto; border-radius: 10px; flex: none; }}
.noco-title {{ font-size: 2.6rem; font-weight: 700; line-height: 1.1; color: #F2F7F8;
  margin: 0 0 0.45rem; }}
.noco-tagline {{ font-size: 1.3rem; line-height: 1.35; color: #E4EDEF; margin: 0 0 0.35rem; }}
.noco-sub {{ color: #9FB3BA; font-size: 0.95rem; line-height: 1.4; }}
.noco-card-title {{ font-size: 1.25rem; font-weight: 700; color: {ACCENT};
  margin: 0.2rem 0 0.6rem; }}
.noco-card-text {{ color: #C9D6DA; line-height: 1.55; margin: 0 0 0.9rem; min-height: 4.7em; }}
.noco-section {{ font-size: 1.25rem; font-weight: 700; color: {ACCENT};
  margin: 1.2rem 0 0.2rem; }}
.noco-steps {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.2rem; }}
.noco-step {{ background: {PANEL_BG}; border-radius: 12px; padding: 1.1rem 1.2rem 1.2rem;
  border-top: 3px solid {ACCENT}; }}
.noco-step .num {{ color: {ACCENT}; font-size: 1.6rem; font-weight: 700; line-height: 1;
  display: block; margin-bottom: 0.6rem; }}
.noco-step .head {{ color: #F2F7F8; font-weight: 700; display: block; margin-bottom: 0.4rem; }}
.noco-step .body {{ color: #C9D6DA; line-height: 1.55; }}
.noco-foot {{ color: #7F949B; font-size: 0.85rem; margin-top: 1.4rem; padding-top: 0.9rem;
  border-top: 1px solid #1F3640; }}
div[data-testid="stPageLink"] a {{ background: {ACCENT}; border-radius: 8px;
  padding: 0.45rem 1rem; }}
div[data-testid="stPageLink"] a p {{ color: #0B1418 !important; font-weight: 600; }}
@media (max-width: 900px) {{ .noco-steps {{ grid-template-columns: 1fr; }}
  .noco-hero {{ flex-direction: column; align-items: flex-start; }} }}
</style>
"""

_STEPS = (
    ("1", "Type a Buffalo address", "or open the prospect map of the whole district."),
    (
        "2",
        "Check the building facts",
        "footprint, perimeter, floors and use, each with its public source and confidence.",
    ),
    (
        "3",
        "Get the estimate and report",
        "savings, incentive and payback from NOCO's own calculator, then download the "
        "customer or manager report.",
    ),
)


def _logo_tag() -> str:
    if not LOGO.is_file():
        return ""
    data = base64.b64encode(LOGO.read_bytes()).decode("ascii")
    return f"<img src='data:image/png;base64,{data}' alt='NOCO logo'>"


def _card(title: str, text: str, page: st.Page, label: str, icon: str) -> None:
    with st.container(border=True):
        st.markdown(
            f"<div class='noco-card-title'>{escape(title)}</div>"
            f"<div class='noco-card-text'>{escape(text)}</div>",
            unsafe_allow_html=True,
        )
        st.page_link(page, label=label, icon=icon)


def home() -> None:
    """Landing page: what NOCO Scout does and where to click."""
    apply_style()
    st.markdown(_HOME_CSS, unsafe_allow_html=True)
    st.markdown(
        f"<div class='noco-hero'>{_logo_tag()}<div>"
        "<div class='noco-title'>NOCO Scout</div>"
        "<div class='noco-tagline'>From an address to a customer-ready quote in seconds.</div>"
        "<div class='noco-sub'>Buffalo, NY · commercial wall insulation · public building data"
        " + NOCO's own savings calculator</div></div></div>",
        unsafe_allow_html=True,
    )
    if offline_mode():
        st.info("Offline mode: saved Buffalo buildings only; the map has no basemap.")

    quote_card, map_card = st.columns(2, gap="large")
    with quote_card:
        _card(
            "Address to Quote",
            "One building: type an address, see its 3D footprint and sourced facts, then "
            "estimate savings, incentive and payback and download a one-page customer report.",
            address_page,
            "Open Address to Quote",
            ":material/search:",
        )
    with map_card:
        _card(
            "Prospect Map",
            "The whole district: rank hundreds of Buffalo buildings by savings on a 3D map, "
            "hover for sources, click for details, export the manager report and CSV.",
            prospect_page,
            "Open Prospect Map",
            ":material/map:",
        )

    steps = "".join(
        f"<div class='noco-step'><span class='num'>{number}</span>"
        f"<span class='head'>{escape(title)}</span><span class='body'>{escape(text)}</span></div>"
        for number, title, text in _STEPS
    )
    st.markdown(
        f"<div class='noco-section'>How it works</div><div class='noco-steps'>{steps}</div>"
        f"<div class='noco-foot'>{escape(OSM_ATTRIBUTION)} · City of Buffalo assessment roll · "
        "US Census geocoder · Estimates, not quotes: a NOCO site visit confirms them.</div>",
        unsafe_allow_html=True,
    )


st.set_page_config(page_title="NOCO Scout", layout="wide")
navigation = st.navigation(
    [
        st.Page(home, title="Home", icon=":material/home:", url_path="home", default=True),
        address_page,
        prospect_page,
        st.Page(
            "streamlit_app.py",
            title="AI site notes",
            icon=":material/description:",
            url_path="AI_site_notes",
        ),
    ]
)
navigation.run()
