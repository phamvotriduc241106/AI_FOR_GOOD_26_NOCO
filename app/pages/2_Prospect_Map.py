"""Source-labelled Buffalo building map and ranked prospect view."""

from __future__ import annotations

import streamlit as st
from pages.noco_shared import (
    _optional_module,
    customer_report_button,
    load_buildings,
    offline_mode,
    rank_buildings,
    render_map,
    show_estimate,
    show_fact_panel,
)

from features.noco_scout.contract import OSM_ATTRIBUTION, Assumptions, Prospect

st.set_page_config(page_title="Prospect Map · NOCO", layout="wide")

st.title("Prospect Map")
st.caption("Buffalo, NY · ranked insulation opportunities from saved public building data")

buildings, synthetic = load_buildings()
if not buildings:
    st.error("No saved Buffalo buildings are available.")
    st.stop()
if synthetic:
    st.warning("SYNTHETIC SAMPLE: these five buildings are made up, not real prospects.")
if offline_mode():
    st.info("Offline mode: no network lookup and no basemap. Building polygons remain interactive.")

use_classes = sorted({facts.use_class for facts in buildings if facts.use_class})
filter_col, savings_col, count_col = st.columns(3)
with filter_col:
    selected_use = st.selectbox("Building use", ["All", *use_classes])
with savings_col:
    minimum_savings = st.number_input("Minimum annual savings (USD)", min_value=0.0, value=0.0)
with count_col:
    top_count = st.slider("Top buildings", 1, len(buildings), min(25, len(buildings)))

with st.expander("ILLUSTRATIVE NOCO cost and margin inputs"):
    use_cost = st.toggle("Enter an illustrative installed cost", value=False)
    cost_per_sqft = (
        st.number_input("Installed cost per insulated wall sq ft (USD)", min_value=0.0, value=8.0)
        if use_cost
        else None
    )
    use_margin = st.toggle("Enter an illustrative NOCO margin", value=False)
    margin_pct = st.slider("NOCO margin fraction", 0.0, 0.5, 0.2, 0.01) if use_margin else None

assumptions = Assumptions(cost_per_sqft=cost_per_sqft, margin_pct=margin_pct)
ranked = rank_buildings(buildings, assumptions)
filtered = [
    prospect
    for prospect in ranked
    if (selected_use == "All" or prospect.facts.use_class == selected_use)
    and prospect.result.annual_cost_savings >= minimum_savings
][:top_count]

if st.button("Show potential customers", type="primary"):
    st.session_state["noco_show_potential"] = True
show_potential = st.session_state.get("noco_show_potential", False)

map_col, detail_col = st.columns([2, 1])
with map_col:
    st.subheader("Buffalo buildings in 3D")
    clicked = render_map(
        filtered,
        key="noco_prospect_map",
        ranked=show_potential,
        height=620,
    )
    st.caption(
        "Blue → orange: lower → higher annual savings, calculated from NOCO inputs and GIS. "
        "3D height follows sourced floors. Hover for sources; click for details. " + OSM_ATTRIBUTION
    )

with detail_col:
    if not show_potential:
        st.info("Click 'Show potential customers' to rank the saved Buffalo buildings.")
    elif not filtered:
        st.info("No building matches these filters.")
    else:
        st.subheader("Building details")
        choice = st.selectbox(
            "Select a building",
            range(len(filtered)),
            format_func=lambda index: f"#{filtered[index].rank} {filtered[index].facts.address}",
        )
        prospect = clicked or filtered[choice]
        st.write(f"**#{prospect.rank} · {prospect.facts.address}**")
        show_fact_panel(prospect.facts)
        show_estimate(prospect)
        opportunity = prospect.opportunity
        st.caption(
            f"Utility: {opportunity.utility} [noco_sheet] · "
            f"Program: {opportunity.incentive_program or 'not confirmed'} [noco_sheet reference]"
        )
        st.write(f"Current supplier: {opportunity.current_supplier}")
        revenue = (
            f"${opportunity.project_revenue:,.0f}"
            if opportunity.project_revenue is not None
            else "needs NOCO cost"
        )
        profit = (
            f"${opportunity.estimated_profit:,.0f}"
            if opportunity.estimated_profit is not None
            else "needs NOCO margin"
        )
        st.write(f"NOCO revenue (ILLUSTRATIVE): {revenue}")
        st.write(f"NOCO profit (ILLUSTRATIVE): {profit}")
        customer_report_button(prospect)

if show_potential and filtered:
    st.subheader("Ranked prospects")

    def _row(prospect: Prospect) -> dict[str, str]:
        return {
            "Rank · calculated": str(prospect.rank),
            "Address": prospect.facts.address,
            "Use · assessor/OSM": prospect.facts.use_class or "unknown",
            "Annual savings · NOCO + GIS": f"${prospect.result.annual_cost_savings:,.0f}",
            "Incentive · NOCO sheet": f"${prospect.result.incentive:,.0f}",
            "Payback · ILLUSTRATIVE cost": (
                f"{prospect.result.simple_payback_years:.1f} years"
                if prospect.result.simple_payback_years is not None
                else "needs cost"
            ),
        }

    st.dataframe([_row(prospect) for prospect in filtered], hide_index=True, width="stretch")
    report = _optional_module("features.noco_scout.report")
    left, right = st.columns(2)
    with left:
        if report is None:
            st.button("Download manager report (HTML)", disabled=True, help="Available after T10.")
        else:
            st.download_button(
                "Download manager report (HTML)",
                report.render_manager_report(filtered, assumptions),
                file_name="noco-manager-report.html",
                mime="text/html",
            )
    with right:
        if report is None:
            st.button("Download prospect CSV", disabled=True, help="Available after T10.")
        else:
            st.download_button(
                "Download prospect CSV",
                report.prospects_to_csv(filtered),
                file_name="noco-prospects.csv",
                mime="text/csv",
            )
