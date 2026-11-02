"""Warehouse Inventory Control Tower – premium Streamlit dashboard.

Uses the existing sample workbook / inventory_agent.py data model:
Warehouses, Products, Warehouse_Stock, Plant_Stock, Shipments.
Run: python -m streamlit run app.py
"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from inventory_agent import (
    active_shipments,
    answer_question,
    load_inventory,
    metrics,
    plant_allocations,
    stock_summary,
)

st.set_page_config(
    page_title="Warehouse Control Tower",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# UI only: the stock calculations are performed by the validated inventory_agent.py.
st.markdown(
    """
<style>
:root { color-scheme: dark; }
.stApp { background: #081426; color: #edf5ff; }
[data-testid="stSidebar"] { background: #101f36; border-right: 1px solid #243954; }
[data-testid="stSidebar"] * { color: #e8f1ff; }
[data-testid="stHeader"] { background: rgba(8,20,38,.89); }
.block-container { padding-top: 1.15rem; padding-bottom: 2.6rem; max-width: 1550px; }
h1, h2, h3 { letter-spacing: -0.02em; }
.hero {
  position: relative; overflow: hidden; border: 1px solid #31537b;
  background: linear-gradient(116deg, #102447 5%, #134779 54%, #167da1 100%);
  border-radius: 22px; padding: 28px 31px; margin-bottom: 19px;
  box-shadow: 0 14px 35px rgba(1,7,20,.23);
}
.hero:after {
  content: ""; position: absolute; width: 270px; height: 270px; right: -50px; top: -118px;
  border-radius: 100%; background: radial-gradient(circle, rgba(92,235,241,.29), rgba(92,235,241,0) 70%);
}
.hero .eyebrow { font-weight: 800; font-size: 12px; color: #a1f5e8; letter-spacing: 3px; }
.hero h1 { font-size: clamp(27px, 3vw, 42px); color: white; margin: 7px 0 8px; line-height: 1.14; }
.hero p { color: #cfe9fa; margin: 0; max-width: 760px; font-size: 15px; }
.hero .hero-icon { position: absolute; right: 43px; top: 38px; font-size: 66px; opacity: .42; }
.kpi { background: linear-gradient(155deg,#152843,#122039); border: 1px solid #2a4563;
  border-radius: 17px; padding: 16px 17px; min-height: 123px;
  box-shadow: 0 6px 20px rgba(0,0,0,.1); margin-bottom: 9px; }
.kpi .meta { font-size: 12px; color: #aabdd6; font-weight: 650; letter-spacing:.3px; }
.kpi .value { font-size: clamp(25px,2.3vw,36px); color: #fff; font-weight: 850; margin: 8px 0 3px; }
.kpi .note { font-size: 11px; color: #92a9c5; }
.kpi .emoji { float: right; font-size: 20px; }
.small-tag { display:inline-block; border:1px solid #28537e; background:#112b4a; color:#a9dcfb;
 border-radius:99px; font-size:12px; padding:6px 11px; margin:2px 6px 14px 0; }
.section-title {font-size:20px; font-weight:780; margin:19px 0 11px; color:#eaf5ff;}
[data-testid="stTabs"] button {color: #d2e4f6; font-weight: 650;}
[data-testid="stTabs"] [aria-selected="true"] {color:#63dbf3;}
[data-testid="stDataFrame"], [data-testid="stPlotlyChart"] {border-radius:12px;}
[data-testid="stFileUploader"] {border-radius:10px;}
[data-testid="stChatMessage"] {border:1px solid #233c58; border-radius:14px;}
hr {border-color: #28415c !important;}
@media (max-width:800px){.hero .hero-icon{display:none;}.hero{padding:21px;}}
</style>
""",
    unsafe_allow_html=True,
)

SAMPLE_FILE = Path(__file__).resolve().parent / "Warehouse_Inventory_Sample.xlsx"

with st.sidebar:
    st.markdown("### 📦 CONTROL CENTER")
    st.caption("WAREHOUSE INTELLIGENCE")
    st.divider()
    uploaded = st.file_uploader("Upload inventory workbook", type=["xlsx"])
    st.caption("Uses the included sample workbook until you upload your own.")
    st.divider()

try:
    inv = load_inventory(uploaded if uploaded is not None else SAMPLE_FILE)
except Exception as exc:
    st.error(f"Unable to open the inventory workbook: {exc}")
    st.info("This dashboard expects these sheets: Warehouses, Products, Warehouse_Stock, Plant_Stock and Shipments. Please use the included template.")
    st.stop()

wh_options = {"All warehouses": None}
wh_options.update({f"{row.Warehouse_Name} ({row.Warehouse_ID})": row.Warehouse_ID for _, row in inv.warehouses.iterrows()})
sku_options = {"All products": None}
sku_options.update({f"{row.SKU}  ·  {row.Product_Name}": row.SKU for _, row in inv.products.iterrows()})

with st.sidebar:
    st.markdown("### 🔎 Filters")
    wh_label = st.selectbox("Warehouse", list(wh_options))
    sku_label = st.selectbox("Product / SKU", list(sku_options))
    warehouse_id = wh_options[wh_label]
    sku = sku_options[sku_label]
    st.divider()
    ai_enabled = st.checkbox("Optional AI explanations", value=False)
    st.caption("Uses verified local calculations. Optional AI sends your question and the verified answer to OpenAI when an API key is configured.")
    st.caption("📅 ETA reference date: " + inv.snapshot.strftime("%d %b %Y"))
    st.caption("🟢 " + ("Uploaded workbook" if uploaded else "Demo workbook"))

m = metrics(inv, warehouse_id, sku)
summary = stock_summary(inv, warehouse_id, sku)
shipments = active_shipments(inv, warehouse_id, sku)
plants = plant_allocations(inv, warehouse_id, sku)

st.markdown(
    """
<div class="hero">
  <div class="eyebrow">OPERATIONS / LIVE VISIBILITY FROM WORKBOOK</div>
  <h1>Warehouse Inventory Control Tower</h1>
  <p>Monitor warehouse availability, plant inventory, goods in transit and shipment ETAs in one modern control center.</p>
  <div class="hero-icon">🏭🚚</div>
</div>
""",
    unsafe_allow_html=True,
)
st.markdown(
    f'<span class="small-tag">📍 {"All warehouses" if warehouse_id is None else wh_label}</span>'
    f'<span class="small-tag">📦 {"All SKUs" if sku is None else sku}</span>'
    f'<span class="small-tag">🗓️ {inv.snapshot:%d %b %Y}</span>',
    unsafe_allow_html=True,
)


def kpi_card(label: str, value: int, emoji: str, note: str = "units") -> None:
    st.markdown(
        f'<div class="kpi"><span class="emoji">{emoji}</span>'
        f'<div class="meta">{label}</div><div class="value">{value:,}</div>'
        f'<div class="note">{note}</div></div>',
        unsafe_allow_html=True,
    )

cards = st.columns(3)
with cards[0]:
    kpi_card("AVAILABLE AT WAREHOUSE", m["available"], "🏬")
with cards[1]:
    kpi_card("GOODS IN TRANSIT", m["transit"], "🚚")
with cards[2]:
    kpi_card("GOODS AT PLANT", m["plant"], "🏭")

cards2 = st.columns(3)
with cards2[0]:
    kpi_card("ARRIVING IN 7 DAYS", m["incoming_7d"], "📅", "pending units with ETA in next 7 days")
with cards2[1]:
    kpi_card("DELAYED SHIPMENTS", m["delayed_count"], "⚠️", "shipments with ETA already passed")
with cards2[2]:
    kpi_card("7-DAY PROJECTED STOCK", m["projected_7d"], "📈", "available + inbound due in 7 days")

PLOT_BG = "rgba(0,0,0,0)"
FONT = "#c9d9ee"


def finish_chart(fig, height=340):
    fig.update_layout(
        height=height,
        paper_bgcolor=PLOT_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=FONT, family="Arial"),
        margin=dict(l=18, r=18, t=45, b=15),
        legend=dict(orientation="h", y=-0.20, x=0.0),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(gridcolor="rgba(133,169,215,.13)", zeroline=False),
    )
    return fig


main_tab, transit_tab, plant_tab, chat_tab = st.tabs([
    "📊 Overview", "🚚 Shipments & ETA", "🏭 Plant Inventory", "🤖 Inventory Agent"
])

with main_tab:
    st.markdown('<div class="section-title">Inventory analytics</div>', unsafe_allow_html=True)
    left, right = st.columns([1.35, 1])
    with left:
        by_warehouse = summary.groupby("Warehouse_Name", as_index=False)[["Available", "In_Transit", "At_Plant"]].sum()
        if not by_warehouse.empty:
            melted = by_warehouse.melt(id_vars="Warehouse_Name", var_name="Stock Stage", value_name="Units")
            fig = px.bar(
                melted,
                x="Warehouse_Name", y="Units", color="Stock Stage", barmode="group",
                color_discrete_map={"Available":"#50d7ec", "In_Transit":"#fdb85b", "At_Plant":"#a99cff"},
                title="Stock by warehouse & stage", text_auto=True,
            )
            fig.update_traces(textposition="outside", cliponaxis=False)
            fig.update_xaxes(title_text="")
            fig.update_yaxes(title_text="Units")
            st.plotly_chart(finish_chart(fig), width="stretch")
        else:
            st.info("No warehouse stock for these filters.")
    with right:
        fig = go.Figure(data=[go.Pie(
            labels=["Warehouse available", "In transit", "At plant"],
            values=[m["available"], m["transit"], m["plant"]],
            hole=0.69,
            marker=dict(colors=["#50d7ec", "#fdb85b", "#a99cff"]),
            textinfo="percent+label",
            sort=False,
        )])
        fig.update_layout(title="Inventory across supply stages", showlegend=False)
        fig.add_annotation(text="STOCK<br>STAGES", x=0.5, y=0.5, showarrow=False,
                           font=dict(size=17, color="#e5f5ff"))
        st.plotly_chart(finish_chart(fig), width="stretch")

    st.markdown('<div class="section-title">Warehouse stock details</div>', unsafe_allow_html=True)
    stock_cols = ["Warehouse_Name", "SKU", "Product_Name", "On_Hand", "Reserved", "Available", "In_Transit", "At_Plant", "Due_7_Days", "Projected_Available_7_Days", "Reorder_Level", "Low_Stock"]
    st.dataframe(summary[stock_cols], width="stretch", hide_index=True, height=340)
    st.download_button("⬇️ Download stock report", summary[stock_cols].to_csv(index=False).encode("utf-8"),
                       file_name="warehouse_stock_report.csv", mime="text/csv")
    shortage_count = int(summary["Low_Stock"].sum())
    if shortage_count:
        st.warning(f"⚠️ {shortage_count} warehouse/SKU combinations are below the reorder level.")
    st.caption("Available stock excludes reserved items, goods at plant, and goods in transit. The 7-day projection excludes outgoing demand.")

with transit_tab:
    st.markdown('<div class="section-title">Shipment tracking & ETA timeline</div>', unsafe_allow_html=True)
    if shipments.empty:
        st.info("No open in-transit shipments match your filters.")
    else:
        timeline = shipments.loc[shipments["ETA"].notna()].copy()
        if not timeline.empty:
            eta_chart = timeline.groupby("ETA", as_index=False)["Pending_Qty"].sum()
            fig = px.bar(eta_chart, x="ETA", y="Pending_Qty", text_auto=True,
                         title="Incoming units by expected arrival date", color_discrete_sequence=["#50d7ec"])
            fig.update_xaxes(title_text="Estimated arrival")
            fig.update_yaxes(title_text="Pending units")
            st.plotly_chart(finish_chart(fig, 340), width="stretch")
        cols = ["Shipment_ID", "Warehouse_Name", "SKU", "Origin_Plant", "Qty_Shipped", "Qty_Received", "Pending_Qty", "Dispatch_Date", "ETA", "ETA_Status"]
        st.dataframe(shipments[cols], hide_index=True, width="stretch", height=410)
        st.download_button("⬇️ Download shipment report", shipments[cols].to_csv(index=False).encode("utf-8"),
                           file_name="shipment_eta_report.csv", mime="text/csv")
        if m["delayed_count"]:
            st.error(f"🚨 {m['delayed_count']} shipment(s) are past their recorded ETA.")
    st.caption("Shipment ETA dates come from your Excel workbook, not GPS or live carrier tracking. Pending = shipped − received.")

with plant_tab:
    st.markdown('<div class="section-title">Plant stock awaiting dispatch</div>', unsafe_allow_html=True)
    if plants.empty:
        st.info("No plant allocations match these filters.")
    else:
        plant_breakdown = plants.groupby("Plant_Name", as_index=False)["Qty_Ready"].sum()
        fig = px.bar(plant_breakdown, x="Plant_Name", y="Qty_Ready", color_discrete_sequence=["#a99cff"],
                     text_auto=True, title="Units ready at each plant")
        fig.update_xaxes(title_text="")
        fig.update_yaxes(title_text="Ready units")
        st.plotly_chart(finish_chart(fig, 315), width="stretch")
        cols = ["Plant_ID", "Plant_Name", "Warehouse_Name", "SKU", "Product_Name", "Qty_Ready", "Planned_Dispatch_Date"]
        st.dataframe(plants[cols], hide_index=True, width="stretch")
        st.download_button("⬇️ Download plant report", plants[cols].to_csv(index=False).encode("utf-8"),
                           file_name="plant_allocations.csv", mime="text/csv")
    st.caption("Plant goods have not been dispatched and are not available in the warehouse.")

with chat_tab:
    st.markdown('<div class="section-title">Ask your inventory agent</div>', unsafe_allow_html=True)
    st.caption("Questions: 'Show delayed shipments', 'ETA for SKU-101', 'How much available stock in Chennai?' or 'Goods at plant'.")
    for msg in st.session_state.get("messages", []):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    question = st.chat_input("Ask about stock, transit, plant, ETAs or delays")
    if question:
        st.session_state.setdefault("messages", []).append({"role": "user", "content": question})
        response = answer_question(question, inv, warehouse_id, sku)
        if ai_enabled:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                try:
                    from openai import OpenAI
                    client = OpenAI(api_key=api_key)
                    result = client.responses.create(
                        model="gpt-4.1-mini",
                        instructions=("Provide a short, clear operations answer based ONLY on the supplied verified "
                                      "inventory calculation. Do not invent quantities, dates, or ETAs."),
                        input=f"Question: {question}\n\nVerified calculation:\n{response}",
                    )
                    if result.output_text.strip():
                        response = result.output_text
                except Exception as exc:
                    response += f"\n\n_AI explanation unavailable ({type(exc).__name__}); local answer shown._"
            else:
                response += "\n\n_AI mode requested but OPENAI_API_KEY is not configured; local answer shown._"
        st.session_state["messages"].append({"role": "assistant", "content": response})
        st.rerun()

st.divider()
st.caption("📦 Warehouse Control Tower  •  Demo figures are fictional  •  Upload your own Excel workbook to track real inventory. Updates are reflected when you upload the latest file.")
