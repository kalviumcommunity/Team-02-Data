import streamlit as st
import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import analytics
import components
import filters

# ─── Page Configuration ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="CostLens AI",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)
components.inject_global_css()

# ─── Page-level extra styles ──────────────────────────────────────────────────
st.markdown("""
<style>
.home-title {
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(90deg, #6366F1 0%, #10B981 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.03em;
    margin-bottom: 0;
}
.home-sub {
    font-size: 1.05rem;
    color: #64748B;
    margin-bottom: 1.5rem;
    margin-top: 0.25rem;
}
.nav-card {
    background: linear-gradient(135deg, #0F172A, #1E293B);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.75rem;
}
.nav-card-title { font-size:1rem; font-weight:700; color:#C7D2FE; margin-bottom:0.3rem; }
.nav-card-desc  { font-size:0.82rem; color:#64748B; line-height:1.55; }
</style>
""", unsafe_allow_html=True)

# ─── Sidebar Filters ──────────────────────────────────────────────────────────
st.sidebar.markdown(
    "<h2 style='color:#F8FAFC;font-weight:700;margin-bottom:1.25rem;font-size:1.1rem;'>"
    "⚙️ Global Filters</h2>",
    unsafe_allow_html=True,
)

try:
    svc_df = analytics.cost_by_gcp_service()
    gcp_services = sorted(svc_df["service_name"].unique().tolist())
except Exception:
    gcp_services = []

selected_providers = filters.provider_filter()
start_date, end_date = filters.date_range_filter()
selected_service = filters.service_filter(gcp_services)

st.sidebar.markdown("---")
st.sidebar.caption("Filters apply to the summary metrics on this page and cascade to all views.")

# ─── Hero Header ──────────────────────────────────────────────────────────────
st.markdown('<h1 class="home-title">CostLens AI</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="home-sub">Multi-Dimensional Cloud Cost Intelligence &amp; Root-Cause Attribution</p>',
    unsafe_allow_html=True,
)
st.divider()

# ─── Problem Statement Banner ─────────────────────────────────────────────────
st.info(
    "**Problem**: Cloud platforms export billing, telemetry and deployment history as siloed datasets. "
    "Finance teams cannot attribute cost spikes to specific engineering activities. "
    "**CostLens AI** correlates these datasets to expose the root cause of every spend change.",
    icon="🔍",
)

# ─── Live Metric Computation ──────────────────────────────────────────────────
try:
    df_cloud = analytics.flag_anomalies()
except Exception:
    df_cloud = pd.DataFrame()

if not df_cloud.empty:
    df_cloud["timestamp"] = pd.to_datetime(df_cloud["timestamp"])
    df_cloud = df_cloud[df_cloud["cloud_provider"].isin(selected_providers)]
    if start_date and end_date:
        s = pd.to_datetime(start_date)
        e = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        df_cloud = df_cloud[(df_cloud["timestamp"] >= s) & (df_cloud["timestamp"] <= e)]

total_spend     = df_cloud["cost"].sum()        if not df_cloud.empty else 0.0
anomaly_count   = int(df_cloud["anomaly_flag"].sum()) if not df_cloud.empty else 0

savings_potential = 0.0
if "GCP" in selected_providers:
    try:
        opt = analytics.optimisation_candidates()
        if selected_service != "All Services":
            opt = opt[opt["service_name"] == selected_service]
        savings_potential = float(opt["total_cost_usd"].sum())
    except Exception:
        pass

# ─── KPI Row ─────────────────────────────────────────────────────────────────
st.markdown("### 📊 Enterprise Summary")
c1, c2, c3 = st.columns(3)
with c1:
    components.kpi_card("Aggregated Cloud Spend", f"${total_spend:,.2f}", "Filtered scope")
with c2:
    components.anomaly_badge(anomaly_count)
with c3:
    components.kpi_card("Rightsizing Savings Potential", f"${savings_potential:,.2f}", "GCP under-utilized services")

st.divider()

# ─── Navigation Guide ────────────────────────────────────────────────────────
st.markdown("### 🚀 Navigate the Dashboard")
n1, n2, n3 = st.columns(3)

with n1:
    st.markdown("""
    <div class="nav-card">
        <div class="nav-card-title">💼 Executive View</div>
        <div class="nav-card-desc">
            High-level GCP billing totals, multi-cloud daily spend trends,
            anomaly counts, and a 7-day linear cost projection with R² disclosure.
        </div>
    </div>""", unsafe_allow_html=True)

with n2:
    st.markdown("""
    <div class="nav-card">
        <div class="nav-card-title">🛠️ Engineering View</div>
        <div class="nav-card-desc">
            CPU &amp; latency KPIs, provider-level spend breakdown, GCP service cost bar chart,
            price-vs-usage root-cause decomposition table (color-coded), and target-action cost signals.
        </div>
    </div>""", unsafe_allow_html=True)

with n3:
    st.markdown("""
    <div class="nav-card">
        <div class="nav-card-title">💸 FinOps View</div>
        <div class="nav-card-desc">
            Under-utilized GCP service candidates (&lt; 50% avg CPU), rightsizing potential,
            team cost attribution with synthetic-data disclaimer, and CSV exports.
        </div>
    </div>""", unsafe_allow_html=True)

st.divider()

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown(
    "<div style='text-align:center;color:#334155;font-size:0.78rem;padding:0.5rem 0;'>"
    "CostLens AI &nbsp;|&nbsp; Alliance University SPE Sprint 1 &nbsp;|&nbsp; Team 02 &nbsp;|&nbsp; "
    "Statistical-only release — no ML libraries used."
    "</div>",
    unsafe_allow_html=True,
)
