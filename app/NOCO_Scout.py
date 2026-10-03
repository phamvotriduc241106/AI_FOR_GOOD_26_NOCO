"""NOCO Scout: app entry point with a home page and named navigation (task T19).

Run: streamlit run app/NOCO_Scout.py
The pages themselves live in app/pages/ and app/streamlit_app.py; this file only adds the
home page and orders the navigation, so users know where to start.
"""

from __future__ import annotations

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
.block-container {{ padding-top: 3.4rem !important; }}  /* clear Streamlit's top header bar */
.noco-tagline {{ font-size: 1.35rem; color: #E4EDEF; margin: 0.1rem 0 0.2rem; }}
.noco-sub {{ color: #9FB3BA; font-size: 0.95rem; }}
.noco-step {{ background: {PANEL_BG}; border-radius: 10px; padding: 0.8rem 1rem;
  border-top: 3px solid {ACCENT}; height: 100%; }}
.noco-step b {{ color: {ACCENT}; font-size: 1.4rem; display: block; }}
div[data-testid="stPageLink"] a {{ background: {ACCENT}; border-radius: 8px;
  padding: 0.35rem 0.9rem; }}
div[data-testid="stPageLink"] a p {{ color: #0B1418 !important; font-weight: 600; }}
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


def home() -> None:
    """Landing page: what NOCO Scout does and where to click."""
    apply_style()
    st.markdown(_HOME_CSS, unsafe_allow_html=True)

    logo_col, title_col = st.columns([1, 6], vertical_alignment="center")
    if LOGO.is_file():
        logo_col.image(str(LOGO), width=120)
    with title_col:
        st.title("NOCO Scout")
        st.markdown(
            "<div class='noco-tagline'>From an address to a customer-ready quote in seconds."
            "</div><div class='noco-sub'>Buffalo, NY · commercial wall insulation · public "
            "building data + NOCO's own savings calculator</div>",
            unsafe_allow_html=True,
        )
    if offline_mode():
        st.info("Offline mode: saved Buffalo buildings only; the map has no basemap.")

    quote_card, map_card = st.columns(2, gap="medium")
    with quote_card, st.container(border=True):
        st.subheader("Address to Quote")
        st.write(
            "One building: type an address, see its 3D footprint and sourced facts, then "
            "estimate savings, incentive and payback and download a one-page customer report."
        )
        st.page_link(address_page, label="Open Address to Quote", icon=":material/search:")
    with map_card, st.container(border=True):
        st.subheader("Prospect Map")
        st.write(
            "The whole district: rank hundreds of Buffalo buildings by savings on a 3D map, "
            "hover for sources, click for details, export the manager report and CSV."
        )
        st.page_link(prospect_page, label="Open Prospect Map", icon=":material/map:")

    st.subheader("How it works")
    for column, (number, title, text) in zip(st.columns(3, gap="medium"), _STEPS, strict=True):
        column.markdown(
            f"<div class='noco-step'><b>{number}</b><strong>{title}</strong><br>{text}</div>",
            unsafe_allow_html=True,
        )

    st.caption(
        f"{OSM_ATTRIBUTION} · City of Buffalo assessment roll · US Census geocoder · "
        "Estimates, not quotes: a NOCO site visit confirms them."
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
