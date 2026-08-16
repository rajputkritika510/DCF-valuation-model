"""
app.py
--------
Streamlit dashboard for the DCF Valuation Model — v3 (redesign pass).

This pass rebuilds the UI to match a supplied product mockup:
    - Custom top navbar (brand mark + "Saved Models / Help / Deploy").
    - Gradient hero banner with a "PRO" badge and a 3-step pill tracker.
    - "Get Started" panel (shown before a valuation has been run) with a
      what-you'll-get checklist, 4 feature cards, and a privacy notice bar.
    - Sidebar restructured into icon-labeled nav sections: Revenue &
      Margins, Cost & Expenses, Working Capital, Capital Expenditures,
      Financing, Tax & Depreciation, Terminal Value — same underlying
      DCF parameters as before, just grouped the way the mockup groups
      them.
    - File uploader restyled (indigo "Browse Files" button, dashed
      dropzone) to match the mockup's upload card.
    - Keeps the v2.1 dark-theme/contrast fixes (config.toml + explicit
      widget colors) so nothing renders invisible.

Run with:
    streamlit run dashboard/app.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import time
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

from src.data_loader import load_historical_csv
from src.financial_analysis import full_historical_analysis, summarize_historicals
from src.wacc import wacc_breakdown
from src.dcf import DCFModel
from src.sensitivity import sensitivity_table, scenario_analysis, scenario_summary_table
from src.import_parser import smart_load


# ----------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="DCF Analyzer",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------
# CUSTOM CSS
# ----------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header[data-testid="stHeader"] { background: transparent; }

/* ============================================================
   APP-WIDE BASE — dark theme contrast fixes
   ============================================================ */
.stApp {
    background: radial-gradient(1200px 600px at 10% -10%, #16233a55 0%, transparent 60%),
                linear-gradient(180deg, #05070c 0%, #090e17 45%, #0b121e 100%) !important;
}
.stApp, .stApp p, .stApp span, .stApp label, .stApp div { color: #e6edf5; }
h1, h2, h3, h4, h5, h6 { color: #ffffff !important; }

.block-container { padding-top: 1.1rem !important; max-width: 1400px; }

[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label { color: #c9d6e3 !important; font-weight: 600 !important; font-size: 0.86rem !important; }

[data-testid="stSlider"] div[data-baseweb="slider"] > div { color: #cfe0f0; }
[data-testid="stTickBar"] { color: #7d90a8 !important; }
[data-testid="stThumbValue"] { background: #4ade80 !important; color: #06210f !important; font-weight: 700 !important; }

input, .stNumberInput input, .stTextInput input {
    background-color: #101828 !important; color: #ffffff !important;
    border: 1px solid #ffffff26 !important; border-radius: 10px !important;
}
[data-baseweb="select"] > div { background-color: #101828 !important; border: 1px solid #ffffff26 !important; color: #ffffff !important; }
[data-testid="stCheckbox"] label p, [data-testid="stRadio"] label p { color: #dce8f4 !important; }
[data-testid="stCaptionContainer"], .stCaption { color: #8ea0b8 !important; }

[data-testid="stMetric"] { background: #101a2b; border: 1px solid #ffffff14; border-radius: 14px; padding: 0.9rem 1rem; }
[data-testid="stMetricLabel"] p { color: #7d90a8 !important; font-weight: 600 !important; }
[data-testid="stMetricValue"] { color: #ffffff !important; font-weight: 800 !important; }
[data-testid="stMetricDelta"] { color: #4ade80 !important; }

[data-testid="stDataFrame"] { border: 1px solid #ffffff14; border-radius: 12px; overflow: hidden; }

button[data-baseweb="tab"] { color: #93a5bc !important; font-weight: 600 !important; }
button[data-baseweb="tab"][aria-selected="true"] { color: #4ade80 !important; border-bottom-color: #4ade80 !important; }
div[data-baseweb="tab-highlight"] { background-color: #4ade80 !important; }

/* ---------- Sidebar shell ---------- */
section[data-testid="stSidebar"] {
    background: #070b12;
    border-right: 1px solid #ffffff10;
}
section[data-testid="stSidebar"] * { color: #dce8f4; }

/* Sidebar nav-style expanders: flat rows with icon + label + chevron,
   like the mockup's left nav, instead of boxed cards. */
section[data-testid="stSidebar"] details {
    background: transparent !important;
    border: none !important;
    border-radius: 8px !important;
    margin-bottom: 2px;
}
section[data-testid="stSidebar"] details:hover { background: #ffffff08 !important; }
section[data-testid="stSidebar"] summary {
    color: #dce8f4 !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    padding: 0.55rem 0.4rem !important;
}
section[data-testid="stSidebar"] details[open] summary { color: #ffffff !important; }
section[data-testid="stSidebar"] [data-testid="stExpanderDetails"] {
    padding: 0.3rem 0.5rem 0.8rem 0.5rem !important;
    border-left: 1px solid #ffffff14;
    margin-left: 0.6rem;
}

/* File uploader — indigo "Browse files" button + dashed dropzone */
[data-testid="stFileUploaderDropzone"] {
    background: #0c1220 !important;
    border: 1.5px dashed #ffffff2a !important;
    border-radius: 12px !important;
}
[data-testid="stFileUploaderDropzone"] * { color: #9fb0c6 !important; }
[data-testid="stFileUploaderDropzone"] button {
    background: linear-gradient(120deg, #6366f1, #4f46e5) !important;
    color: #ffffff !important; border: none !important; border-radius: 10px !important; font-weight: 700 !important;
}
[data-testid="stFileUploaderDropzone"] button p { color: #ffffff !important; }

/* Sidebar section labels (STEP 1 · DATA SOURCE style) */
.side-label {
    color: #7d90a8 !important; font-size: 0.72rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.07em; margin: 1.1rem 0 0.45rem 0;
}
.side-label.brand { color: #a5b4fc !important; }

/* ---------- Top navbar ---------- */
.topnav {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.5rem 0.2rem 1.1rem 0.2rem;
    border-bottom: 1px solid #ffffff10;
    margin-bottom: 1.4rem;
}
.topnav-right { display: flex; align-items: center; gap: 1.4rem; }
.topnav-link { color: #b7c4d6; font-size: 0.9rem; font-weight: 600; display: inline-flex; align-items: center; gap: 6px; }
.topnav-deploy {
    background: linear-gradient(120deg, #6366f1, #4f46e5);
    color: #ffffff; font-weight: 700; padding: 0.5rem 1.1rem; border-radius: 10px; font-size: 0.88rem;
    display: inline-flex; align-items: center; gap: 6px;
}

/* ---------- Hero ---------- */
.hero {
    background: linear-gradient(115deg, #0b1220 0%, #10233a 40%, #113a34 100%);
    padding: 2.2rem 2.4rem;
    border-radius: 20px;
    margin-bottom: 1.8rem;
    border: 1px solid #ffffff14;
    position: relative;
    overflow: hidden;
    display: flex; align-items: center; gap: 1.8rem;
}
.hero::after {
    content: "";
    position: absolute; top: -50%; right: -8%;
    width: 380px; height: 380px; border-radius: 50%;
    background: radial-gradient(circle, #4ade8022 0%, transparent 70%);
}
.hero-icon {
    flex: 0 0 auto; width: 74px; height: 74px; border-radius: 50%;
    background: radial-gradient(circle at 35% 30%, #1a3a5c, #0c1c30);
    border: 1px solid #60a5fa55;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.8rem; box-shadow: 0 0 0 6px #60a5fa14;
}
.hero-body { flex: 1 1 auto; position: relative; z-index: 1; }
.hero-title-row { display: flex; align-items: center; gap: 12px; }
.hero h1 { color: #ffffff !important; font-weight: 800; font-size: 1.9rem; margin: 0; letter-spacing: -0.02em; }
.hero-pro { background: #6366f1; color: #ffffff !important; font-size: 0.7rem; font-weight: 800; padding: 3px 10px; border-radius: 999px; letter-spacing: 0.03em; }
.hero p.hero-sub { color: #9fb4cc !important; font-size: 0.96rem; margin: 8px 0 0 0; max-width: 640px; }
.hero-steps { display: flex; align-items: center; gap: 12px; margin-top: 1.2rem; flex-wrap: wrap; }
.hero-step {
    background: #0c1524cc; border: 1px solid #ffffff1f; color: #cfe0f0 !important;
    padding: 8px 16px; border-radius: 12px; font-size: 0.85rem; font-weight: 600;
    display: flex; align-items: center; gap: 10px;
}
.hero-step .num {
    width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
    font-size: 0.78rem; font-weight: 800; flex: 0 0 auto;
}
.hero-step.s1 .num { background: #0f2e20; color: #4ade80; border: 1px solid #4ade8055; }
.hero-step.s2 .num { background: #2a1e42; color: #a78bfa; border: 1px solid #a78bfa55; }
.hero-step.s3 .num { background: #10233a; color: #60a5fa; border: 1px solid #60a5fa55; }
.hero-step .step-sub { display: block; color: #7d90a8 !important; font-size: 0.72rem; font-weight: 500; }
.hero-connector { width: 26px; height: 1px; background: #ffffff22; }

/* ---------- Get Started ---------- */
.section-heading { display: flex; align-items: center; gap: 10px; margin: 0 0 0.9rem 0; color: #ffffff !important; font-size: 1.15rem; font-weight: 700; }

.getstarted-card {
    background: linear-gradient(160deg, #101a2b, #0d1524);
    border: 1px solid #ffffff14; border-radius: 18px;
    padding: 1.8rem 2rem; margin-bottom: 1.3rem;
    display: flex; align-items: center; gap: 1.8rem;
}
.getstarted-icon {
    flex: 0 0 auto; width: 68px; height: 68px; border-radius: 18px;
    background: linear-gradient(160deg, #14493f, #0e2c26);
    border: 1px solid #4ade8040;
    display: flex; align-items: center; justify-content: center; font-size: 1.7rem;
}
.getstarted-mid { flex: 1.3 1 auto; }
.getstarted-mid h3 { color: #ffffff !important; font-size: 1.15rem; margin: 0 0 6px 0; }
.getstarted-mid p { color: #96a7bd !important; font-size: 0.92rem; margin: 0; max-width: 460px; }
.getstarted-divider { width: 1px; align-self: stretch; background: #ffffff14; }
.getstarted-list { flex: 1 1 auto; }
.getstarted-list h4 { color: #ffffff !important; font-size: 0.95rem; margin: 0 0 10px 0; }
.getstarted-list ul { list-style: none; margin: 0; padding: 0; }
.getstarted-list li { display: flex; align-items: center; gap: 9px; color: #c3d0e0 !important; font-size: 0.88rem; margin-bottom: 8px; }
.getstarted-list li .tick { color: #4ade80; font-weight: 800; }

/* ---------- Feature cards ---------- */
.feature-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 14px; margin-bottom: 1.3rem; }
.feature-card { background: #0d1524; border: 1px solid #ffffff14; border-radius: 16px; padding: 1.4rem 1.3rem; transition: border-color .15s ease, transform .15s ease; }
.feature-card:hover { border-color: #ffffff2c; transform: translateY(-2px); }
.feature-icon { width: 46px; height: 46px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; margin-bottom: 0.9rem; }
.feature-card h5 { color: #ffffff !important; font-size: 1rem; margin: 0 0 6px 0; }
.feature-card p { color: #8ea0b8 !important; font-size: 0.85rem; margin: 0; line-height: 1.45; }

/* ---------- Privacy bar ---------- */
.privacy-bar {
    display: flex; align-items: center; gap: 12px;
    background: #0d1524; border: 1px solid #ffffff14; border-radius: 14px;
    padding: 1rem 1.3rem; color: #b7c4d6 !important; font-size: 0.88rem; margin-bottom: 1rem;
}
.privacy-bar .shield { color: #4ade80; font-size: 1.1rem; }

/* ---------- KPI cards (dashboard state) ---------- */
.kpi-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 14px; margin-bottom: 1.4rem; }
.kpi-card { background: linear-gradient(160deg, #131c2b, #0f1826); border: 1px solid #ffffff14; border-radius: 16px; padding: 1.1rem 1.3rem; transition: border-color .15s ease, transform .15s ease; }
.kpi-card:hover { border-color: #ffffff2c; transform: translateY(-2px); }
.kpi-label { color: #7d90a8 !important; font-size: 0.78rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 6px; }
.kpi-value { color: #ffffff !important; font-size: 1.55rem; font-weight: 800; font-family: 'JetBrains Mono', monospace; }
.kpi-sub { font-size: 0.8rem; margin-top: 4px; font-weight: 600; }
.kpi-sub.up { color: #4ade80 !important; }
.kpi-sub.down { color: #f87171 !important; }

/* ---------- Verdict badge ---------- */
.verdict-badge { display: inline-flex; align-items: center; gap: 8px; padding: 0.55rem 1.2rem; border-radius: 999px; font-weight: 700; font-size: 0.95rem; margin: 0.6rem 0 1.4rem 0; }
.verdict-under { background: #0f2e20; color: #4ade80 !important; border: 1px solid #4ade8040; }
.verdict-over  { background: #2e1414; color: #f87171 !important; border: 1px solid #f8717140; }

/* ---------- Import / warn banners ---------- */
.import-banner { background: #10233a; border: 1px solid #3b82f660; border-radius: 12px; padding: 0.8rem 1rem; margin-bottom: 0.8rem; font-size: 0.85rem; color: #bfdcff !important; }
.import-banner b { color: #93c5fd !important; }
.warn-banner { background: #2e2410; border: 1px solid #f59e0b60; border-radius: 12px; padding: 0.8rem 1rem; margin-bottom: 0.8rem; font-size: 0.85rem; color: #fde3a8 !important; }

/* ---------- Buttons ---------- */
div[data-testid="stButton"] > button { border-radius: 12px; font-weight: 700; border: none; background: linear-gradient(120deg, #4ade80, #22c55e); color: #06210f !important; transition: transform 0.15s ease; }
div[data-testid="stButton"] > button:hover { transform: translateY(-1px); }
div[data-testid="stButton"] > button p { color: #06210f !important; }
</style>
""", unsafe_allow_html=True)


# ----------------------------------------------------------------------
# TOP NAVBAR
# ----------------------------------------------------------------------
st.markdown("""
<div class="topnav">
    <div style="display:flex; align-items:center; gap:10px;">
        <div style="width:36px;height:36px;border-radius:10px;background:linear-gradient(135deg,#6366f1,#4f46e5);
                    display:flex;align-items:center;justify-content:center;font-size:1rem;">📈</div>
        <span style="color:#ffffff;font-weight:800;font-size:1.05rem;">DCF Analyzer</span>
    </div>
    <div class="topnav-right">
        <span class="topnav-link">🗂️ Saved Models</span>
        <span class="topnav-link">❓ Help</span>
        <span class="topnav-deploy">🚀 Deploy</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# HERO
# ----------------------------------------------------------------------
st.markdown("""
<div class="hero">
    <div class="hero-icon">💲</div>
    <div class="hero-body">
        <div class="hero-title-row">
            <h1>DCF Valuation Model</h1>
            <span class="hero-pro">PRO</span>
        </div>
        <p class="hero-sub">Upload historicals or a finished model, tune the assumptions, and run a full discounted cash flow valuation with sensitivity and scenario analysis.</p>
        <div class="hero-steps">
            <div class="hero-step s1"><span class="num">1</span><span>Add data<span class="step-sub">Upload your data</span></span></div>
            <div class="hero-connector"></div>
            <div class="hero-step s2"><span class="num">2</span><span>Set assumptions<span class="step-sub">Define key inputs</span></span></div>
            <div class="hero-connector"></div>
            <div class="hero-step s3"><span class="num">3</span><span>Run valuation<span class="step-sub">Analyze results</span></span></div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ----------------------------------------------------------------------
# SESSION STATE
# ----------------------------------------------------------------------
if "results" not in st.session_state:
    st.session_state.results = None
if "imported" not in st.session_state:
    st.session_state.imported = None


# ----------------------------------------------------------------------
# SIDEBAR — COMPANY
# ----------------------------------------------------------------------
st.sidebar.markdown('<div class="side-label brand">🏢 Company</div>', unsafe_allow_html=True)
company_name = st.sidebar.text_input("Company Name", "TCS", label_visibility="visible")

# ----------------------------------------------------------------------
# SIDEBAR — STEP 1: DATA
# ----------------------------------------------------------------------
st.sidebar.markdown('<div class="side-label">Step 1 · Data source</div>', unsafe_allow_html=True)
uploaded_file = st.sidebar.file_uploader(
    "Upload historical data OR a finished DCF workbook",
    type=["csv", "xlsx", "xls"],
    help="Works with raw year-by-year financials, or an already-built valuation workbook — the app auto-detects which one you gave it.",
)

hist_df = None
imported_params = {}

if uploaded_file is not None:
    load_result = smart_load(uploaded_file)

    if load_result["mode"] == "historical":
        hist_df = load_result["df"]
        st.sidebar.markdown(
            f'<div class="import-banner">✅ <b>Historical data detected</b> — {len(hist_df)} years loaded from {uploaded_file.name}.</div>',
            unsafe_allow_html=True,
        )

    elif load_result["mode"] == "prebuilt":
        imported_params = load_result["params"]
        found = ", ".join(sorted(imported_params.keys()))
        st.sidebar.markdown(
            f'<div class="import-banner">✅ <b>Pre-built valuation workbook detected</b> — reverse-engineered assumptions from {uploaded_file.name} and pre-filled the sliders below. '
            f'Ratios (growth, margins) are averaged across the years found in your file, so results may differ slightly from the original.</div>',
            unsafe_allow_html=True,
        )
        sample_path = os.path.join(os.path.dirname(__file__), "..", "data", "sample_data.csv")
        hist_df = load_historical_csv(sample_path)

    else:
        st.sidebar.markdown(
            '<div class="warn-banner">⚠️ Could not recognize this file\'s format. Falling back to the bundled sample data — '
            'expected either raw historical columns (year, revenue, ebit, ...) or a workbook with a "Key Assumptions" sheet.</div>',
            unsafe_allow_html=True,
        )
        sample_path = os.path.join(os.path.dirname(__file__), "..", "data", "sample_data.csv")
        hist_df = load_historical_csv(sample_path)
else:
    sample_path = os.path.join(os.path.dirname(__file__), "..", "data", "sample_data.csv")
    hist_df = load_historical_csv(sample_path)
    st.sidebar.caption("Using bundled sample data — upload your own CSV/Excel to replace it.")

summary = summarize_historicals(hist_df)


def imp(key, fallback):
    """Pull a value from imported_params if present, else use the fallback."""
    return imported_params.get(key, fallback)


# ----------------------------------------------------------------------
# SIDEBAR — STEP 2: ASSUMPTIONS (regrouped to match the nav layout)
# ----------------------------------------------------------------------
st.sidebar.markdown('<div class="side-label">Step 2 · Forecast assumptions</div>', unsafe_allow_html=True)

with st.sidebar.expander("📈  Revenue & Margins", expanded=True):
    forecast_years = st.slider("Forecast Horizon (years)", 3, 10, int(imp("forecast_years", 5)))
    revenue_growth = st.slider(
        "Revenue Growth Rate (%)", 0.0, 30.0,
        float(round(imp("revenue_growth", summary["avg_revenue_growth"]) * 100, 1)), 0.5
    ) / 100

with st.sidebar.expander("🧮  Cost & Expenses", expanded=False):
    ebit_margin = st.slider(
        "EBIT Margin (%)", 0.0, 60.0,
        float(round(imp("ebit_margin", summary["avg_ebit_margin"]) * 100, 1)), 0.5
    ) / 100

with st.sidebar.expander("💧  Working Capital", expanded=False):
    nwc_pct = st.slider("Change in NWC (% of Revenue)", 0.0, 10.0, float(round(imp("nwc_pct", 0.01) * 100, 1)), 0.25) / 100

with st.sidebar.expander("🏗️  Capital Expenditures", expanded=False):
    capex_pct = st.slider("Capex (% of Revenue)", 0.0, 15.0, float(round(imp("capex_pct", summary["avg_capex_ratio"]) * 100, 1)), 0.5) / 100

with st.sidebar.expander("💸  Financing (WACC)", expanded=False):
    use_direct_wacc = "wacc" in imported_params
    override_wacc = st.checkbox("Use imported WACC directly (skip CAPM)", value=use_direct_wacc) if use_direct_wacc else False

    if override_wacc:
        wacc = st.slider("WACC (%)", 1.0, 25.0, float(round(imported_params["wacc"] * 100, 2)), 0.05) / 100
        wacc_info = {"cost_of_equity": None, "cost_of_debt_aftertax": None, "wacc": wacc}
    else:
        risk_free_rate = st.slider("Risk Free Rate (%)", 0.0, 15.0, 6.8, 0.1) / 100
        beta = st.slider("Beta", 0.0, 2.5, 0.95, 0.05)
        market_return = st.slider("Expected Market Return (%)", 0.0, 20.0, 11.5, 0.1) / 100
        cost_of_debt = st.slider("Pre-tax Cost of Debt (%)", 0.0, 15.0, 7.5, 0.1) / 100
        market_cap = st.number_input("Market Cap (₹ Cr)", value=1160000.0, step=1000.0)
        total_debt = st.number_input("Total Debt (₹ Cr)", value=8000.0, step=500.0)

with st.sidebar.expander("🧾  Tax & Depreciation", expanded=False):
    tax_rate = st.slider(
        "Tax Rate (%)", 0.0, 40.0,
        float(round(imp("tax_rate", summary["avg_tax_rate"]) * 100, 1)), 0.5
    ) / 100
    da_pct = st.slider("D&A (% of Revenue)", 0.0, 15.0, float(round(imp("da_pct", summary["avg_da_ratio"]) * 100, 1)), 0.5) / 100

with st.sidebar.expander("♾️  Terminal Value", expanded=False):
    terminal_growth = st.slider(
        "Terminal Growth Rate (%)", 0.0, 8.0,
        float(round(imp("terminal_growth", 0.04) * 100, 2)), 0.25
    ) / 100
    net_debt_val = st.number_input("Net Debt (₹ Cr, negative = net cash)", value=float(imp("net_debt", summary["latest_net_debt"])))
    shares_val = st.number_input("Shares Outstanding (Cr)", value=float(imp("shares_outstanding", summary["latest_shares_outstanding"])))
    price_val = st.number_input("Current Market Price (₹)", value=float(imp("current_price", summary["latest_price"])))
    revenue_base_val = st.number_input("Base Revenue (₹ Cr)", value=float(imp("revenue_base", summary["latest_revenue"])))

# WACC depends on tax_rate, which is set in the "Tax & Depreciation" section
# below "Financing" in the sidebar — so it's computed here, after both
# sections have run, using whichever path (direct WACC vs CAPM) applies.
if not override_wacc:
    wacc_info = wacc_breakdown(market_cap, total_debt, risk_free_rate, beta, market_return, cost_of_debt, tax_rate)
    wacc = wacc_info["wacc"]

# ----------------------------------------------------------------------
# SIDEBAR — STEP 3: RUN
# ----------------------------------------------------------------------
st.sidebar.markdown('<div class="side-label">Step 3 · Run</div>', unsafe_allow_html=True)
run_clicked = st.sidebar.button("🚀 Run DCF Valuation", use_container_width=True)
reset_clicked = st.sidebar.button("↺ Reset Results", use_container_width=True)

if reset_clicked:
    st.session_state.results = None

base_params = dict(
    revenue_base=revenue_base_val,
    revenue_growth=revenue_growth,
    ebit_margin=ebit_margin,
    tax_rate=tax_rate,
    da_pct=da_pct,
    capex_pct=capex_pct,
    nwc_pct=nwc_pct,
    wacc=wacc,
    terminal_growth=terminal_growth,
    net_debt=net_debt_val,
    shares_outstanding=shares_val,
    forecast_years=forecast_years,
    current_price=price_val,
)

if run_clicked:
    with st.spinner("Running the DCF engine — forecasting, discounting, valuing..."):
        time.sleep(0.6)
        model = DCFModel(**base_params)
        st.session_state.results = {
            "result": model.run(),
            "base_params": base_params,
            "wacc_info": wacc_info,
            "hist_df": hist_df,
            "company_name": company_name,
        }

# ----------------------------------------------------------------------
# MAIN AREA
# ----------------------------------------------------------------------
if st.session_state.results is None:
    st.markdown('<div class="section-heading">🚀 Get Started</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="getstarted-card">
        <div class="getstarted-icon">⬆️</div>
        <div class="getstarted-mid">
            <h3>Upload your data to begin</h3>
            <p>Upload your historicals or use our sample dataset, tune the assumptions in the sidebar, then run the DCF valuation.</p>
        </div>
        <div class="getstarted-divider"></div>
        <div class="getstarted-list">
            <h4>What you'll get</h4>
            <ul>
                <li><span class="tick">✔</span> Intrinsic value &amp; per-share valuation</li>
                <li><span class="tick">✔</span> Forecast build-up &amp; cash flow projections</li>
                <li><span class="tick">✔</span> Sensitivity heatmap (WACC vs Terminal Growth)</li>
                <li><span class="tick">✔</span> Scenario analysis (Bear / Base / Bull)</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-grid">
        <div class="feature-card">
            <div class="feature-icon" style="background:linear-gradient(160deg,#3730a3,#1e1b4b);color:#a5b4fc;">🗄️</div>
            <h5>Flexible Data Input</h5>
            <p>Upload CSV/XLSX or use sample data to get started quickly.</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon" style="background:linear-gradient(160deg,#1d4ed8,#0c1c3a);color:#93c5fd;">🎚️</div>
            <h5>Custom Assumptions</h5>
            <p>Adjust key drivers and assumptions to reflect your outlook.</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon" style="background:linear-gradient(160deg,#0f7a5c,#0c2c22);color:#6ee7b7;">📈</div>
            <h5>Advanced Analysis</h5>
            <p>Run full DCF with sensitivity heatmaps and scenario comparisons.</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon" style="background:linear-gradient(160deg,#1e3a8a,#0c1c3a);color:#93c5fd;">🛡️</div>
            <h5>Enterprise Grade</h5>
            <p>Secure, fast and built for analysts, investors and finance teams.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="privacy-bar"><span class="shield">🛡️</span> Your data is private and encrypted. Files are processed securely and never shared.</div>
    """, unsafe_allow_html=True)

    st.stop()

# From here on, results exist
state = st.session_state.results
result = state["result"]
base_params = state["base_params"]
wacc_info = state["wacc_info"]
hist_df = state["hist_df"]
company_name = state["company_name"]
wacc = base_params["wacc"]
terminal_growth = base_params["terminal_growth"]

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["🏠 Overview", "📊 Historical Data", "🔮 Forecast & FCFF", "🎯 Sensitivity", "🐻🐂 Scenarios"]
)

# ---------------- TAB 1: OVERVIEW ----------------
with tab1:
    upside_class = "up" if result["upside_pct"] >= 0 else "down"
    upside_sign = "+" if result["upside_pct"] >= 0 else ""

    st.markdown(f"""
    <div class="kpi-row">
        <div class="kpi-card">
            <div class="kpi-label">Intrinsic Value / Share</div>
            <div class="kpi-value">₹{result['value_per_share']:,.2f}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Current Market Price</div>
            <div class="kpi-value">₹{result['current_price']:,.2f}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Upside / Downside</div>
            <div class="kpi-value">{upside_sign}{result['upside_pct']*100:,.2f}%</div>
            <div class="kpi-sub {upside_class}">{'▲ undervalued' if result['upside_pct']>=0 else '▼ overvalued'}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">WACC Used</div>
            <div class="kpi-value">{wacc*100:,.2f}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    badge_class = "verdict-under" if result["verdict"] == "Potentially Undervalued" else "verdict-over"
    icon = "📈" if result["verdict"] == "Potentially Undervalued" else "📉"
    st.markdown(
        f'<span class="verdict-badge {badge_class}">{icon} {result["verdict"]} — {company_name}</span>',
        unsafe_allow_html=True,
    )

    if result["upside_pct"] and result["upside_pct"] > 0.10:
        st.balloons()

    st.markdown("##### 🏢 Enterprise → Equity Value Bridge")
    waterfall = go.Figure(go.Waterfall(
        orientation="v",
        measure=["relative", "relative", "total", "relative", "total"],
        x=["PV of FCFF", "PV of Terminal Value", "Enterprise Value", "Less: Net Debt", "Equity Value"],
        y=[
            result["sum_pv_fcff"], result["pv_terminal_value"], 0,
            -base_params["net_debt"], 0,
        ],
        connector={"line": {"color": "rgba(200,200,200,0.35)"}},
        increasing={"marker": {"color": "#4ade80"}},
        decreasing={"marker": {"color": "#f87171"}},
        totals={"marker": {"color": "#60a5fa"}},
    ))
    waterfall.update_layout(
        template="plotly_dark", height=420, margin=dict(t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#e6edf5"),
    )
    st.plotly_chart(waterfall, use_container_width=True)

    st.caption(
        "⚠️ This is not a guaranteed Buy/Sell recommendation. DCF valuation is highly "
        "sensitive to assumptions — check the Sensitivity and Scenario tabs before drawing conclusions."
    )

# ---------------- TAB 2: HISTORICAL DATA ----------------
with tab2:
    st.markdown("##### 📂 Historical Financials")
    st.dataframe(full_historical_analysis(hist_df), use_container_width=True)

    fig_hist = px.bar(
        hist_df, x="year", y="revenue", text_auto=".2s",
        title="Historical Revenue Trend", color_discrete_sequence=["#60a5fa"],
    )
    fig_hist.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter", color="#e6edf5"))
    st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown("##### 💸 WACC Breakdown")
    wc1, wc2, wc3 = st.columns(3)
    ke_display = f"{wacc_info['cost_of_equity']*100:.2f}%" if wacc_info.get("cost_of_equity") is not None else "n/a (direct WACC)"
    kd_display = f"{wacc_info['cost_of_debt_aftertax']*100:.2f}%" if wacc_info.get("cost_of_debt_aftertax") is not None else "n/a (direct WACC)"
    wc1.metric("Cost of Equity (Ke)", ke_display)
    wc2.metric("After-tax Cost of Debt", kd_display)
    wc3.metric("Final WACC", f"{wacc_info['wacc']*100:.2f}%")

# ---------------- TAB 3: FORECAST & FCFF ----------------
with tab3:
    years_labels = [f"Year {i+1}" for i in range(base_params["forecast_years"])]
    fcff_df = pd.DataFrame(result["fcff_details"])
    fcff_df.insert(0, "Period", years_labels)

    st.markdown("##### 🔮 Forecasted Revenue, EBIT & FCFF")
    st.dataframe(fcff_df.style.format({c: "{:,.0f}" for c in fcff_df.columns if c != "Period"}),
                 use_container_width=True)

    fig_fcff = go.Figure()
    fig_fcff.add_trace(go.Bar(x=years_labels, y=result["fcff_list"], name="FCFF", marker_color="#4ade80"))
    fig_fcff.add_trace(go.Scatter(x=years_labels, y=result["pv_fcff_list"], name="PV of FCFF",
                                   mode="lines+markers", line=dict(color="#facc15", width=3)))
    fig_fcff.update_layout(
        title="Free Cash Flow to Firm — Forecast vs Present Value",
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=430,
        font=dict(family="Inter", color="#e6edf5"),
    )
    st.plotly_chart(fig_fcff, use_container_width=True)

# ---------------- TAB 4: SENSITIVITY ----------------
with tab4:
    st.markdown("##### 🎯 Sensitivity: WACC vs Terminal Growth")
    st.caption("Shows how the intrinsic value per share shifts as your two riskiest assumptions change.")

    wacc_range = [max(0.01, wacc + d) for d in (-0.01, -0.005, 0, 0.005, 0.01)]
    growth_range = [max(0.0, terminal_growth + d) for d in (-0.01, -0.005, 0, 0.005, 0.01)]

    sens_params = {k: v for k, v in base_params.items() if k not in ("wacc", "terminal_growth")}
    sens_df = sensitivity_table(sens_params, wacc_range, growth_range)

    fig_heat = px.imshow(
        sens_df.values, x=sens_df.columns, y=sens_df.index,
        text_auto=True, color_continuous_scale="RdYlGn", aspect="auto",
        labels=dict(x="Terminal Growth", y="WACC", color="Value/Share"),
    )
    fig_heat.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", height=450, font=dict(family="Inter", color="#e6edf5"))
    st.plotly_chart(fig_heat, use_container_width=True)
    st.dataframe(sens_df, use_container_width=True)

# ---------------- TAB 5: SCENARIOS ----------------
with tab5:
    st.markdown("##### 🐻 Bear / 📊 Base / 🐂 Bull Scenario Comparison")

    bear_overrides = {
        "revenue_growth": max(0.0, revenue_growth - 0.03),
        "ebit_margin": max(0.01, ebit_margin - 0.03),
        "wacc": wacc + 0.01,
        "terminal_growth": max(0.0, terminal_growth - 0.01),
    }
    bull_overrides = {
        "revenue_growth": revenue_growth + 0.03,
        "ebit_margin": ebit_margin + 0.03,
        "wacc": max(0.02, wacc - 0.01),
        "terminal_growth": terminal_growth + 0.01,
    }

    scenarios = scenario_analysis(base_params, bear_overrides, bull_overrides)
    scen_df = scenario_summary_table(scenarios)

    fig_scen = px.bar(
        scen_df, x="Scenario", y="Value per Share", color="Scenario", text="Value per Share",
        color_discrete_map={"Bear": "#f87171", "Base": "#60a5fa", "Bull": "#4ade80"},
    )
    fig_scen.add_hline(y=result["current_price"], line_dash="dash", line_color="white",
                        annotation_text="Current Market Price")
    fig_scen.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)", height=430, showlegend=False, font=dict(family="Inter", color="#e6edf5"))
    st.plotly_chart(fig_scen, use_container_width=True)
    st.dataframe(scen_df, use_container_width=True)

st.markdown("---")
st.caption(f"Built with ❤️ using Python, Streamlit & Plotly · DCF Valuation Model · Results computed at your last click of 🚀 Run")