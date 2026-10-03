"""Buffalo address lookup and NOCO insulation estimate."""

from __future__ import annotations

import httpx
import streamlit as st
from pages.noco_shared import (
    DEMO_COST_PER_SQFT,
    DEMO_NOTE,
    apply_style,
    customer_report_button,
    find_building,
    load_buildings,
    make_prospect,
    offline_mode,
    render_map,
    show_estimate,
    show_fact_panel,
)

from features.noco_scout.contract import Assumptions

st.set_page_config(page_title="Address to Quote · NOCO", layout="wide")
apply_style()

st.title("Address to Quote")
st.caption("Buffalo, NY · public building facts → deterministic insulation estimate")

buildings, synthetic = load_buildings()
if synthetic:
    st.warning("SYNTHETIC SAMPLE: five made-up Buffalo buildings. Public data has not landed yet.")
if offline_mode():
    st.info("Offline mode: address search uses saved buildings only; the map has no basemap.")

default_address = buildings[0].address if buildings else ""
address = st.text_input("Buffalo building address", value=default_address)
if st.button("Find building", type="primary"):
    try:
        found = find_building(address, buildings)
    except (httpx.HTTPError, OSError, ValueError) as exc:
        found = None
        st.error(f"Address lookup failed: {exc}")
    if found is None:
        st.session_state.pop("noco_address_facts", None)
        st.session_state["noco_address_missing"] = True
    else:
        st.session_state["noco_address_facts"] = found
        st.session_state["noco_address_missing"] = False
        st.session_state["noco_address_estimated"] = False

if st.session_state.get("noco_address_missing"):
    st.warning("Address not found in the saved Buffalo buildings. Try a listed address.")
    st.stop()

facts = st.session_state.get("noco_address_facts", buildings[0] if buildings else None)
if facts is None:
    st.error("No building is available to estimate.")
    st.stop()

use_cost = st.toggle("Enter an ILLUSTRATIVE installed cost", value=True)
cost_per_sqft = (
    st.number_input(
        ":red[Installed cost per insulated wall sq ft (USD) · DEMO]",
        min_value=0.0,
        value=DEMO_COST_PER_SQFT,
        key="noco_demo_cost_address",
    )
    if use_cost
    else None
)
assumptions = Assumptions(cost_per_sqft=cost_per_sqft)
prospect = make_prospect(facts, assumptions)
st.markdown(f":red[{DEMO_NOTE}]")

map_col, facts_col = st.columns([3, 2], gap="medium")
with map_col:
    st.subheader("Building footprint in 3D")
    render_map(
        [prospect],
        key="noco_address_map",
        center=(facts.lat, facts.lon),
    )
    st.caption("3D height uses sourced floors and floor height. Hover for sources.")
with facts_col:
    st.subheader("Facts and confidence")
    show_fact_panel(facts)

if st.button("Estimate insulation upgrade"):
    st.session_state["noco_address_estimated"] = True
if st.session_state.get("noco_address_estimated"):
    st.subheader("Insulation estimate")
    show_estimate(prospect)
    customer_report_button(prospect)
