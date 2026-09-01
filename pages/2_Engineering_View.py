import streamlit as st
import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import analytics
import components
import filters

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(layout="wide", page_title="Engineering View — CostLens AI")
components.inject_global_css()
st.markdown("""
<style>
.page-title {
    font-size: 2.4rem; font-weight: 800; letter-spacing: -0.02em;
    background: linear-gradient(90deg, #3B82F6 0%, #06B6D4 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 0;
}
.page-sub { font-size: 0.9rem; color: #64748B; margin-top: 0.2rem; margin-bottom: 1rem; }
.section-header {
    font-size: 1rem; font-weight: 700; color: #94A3B8;
    text-transform: uppercase; letter-spacing: 0.07em; margin: 1.5rem 0 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# ─── Sidebar Filters ──────────────────────────────────────────────────────────
st.sidebar.markdown(
    "<h2 style='color:#F8FAFC;font-weight:700;margin-bottom:1.25rem;font-size:1.1rem;'>"
    "⚙️ Engineering Filters</h2>",
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
st.sidebar.caption("Filters update all charts and tables on this page in real-time.")

# ─── Page Header ─────────────────────────────────────────────────────────────
st.markdown('<h1 class="page-title">🛠️ Engineering View</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="page-sub">Resource Utilisation Profiles · Price-vs-Usage Attribution · Deployment Cost Signals</p>',
    unsafe_allow_html=True,
)
st.divider()

# ─── Load & Filter Telemetry Data ────────────────────────────────────────────
try:
    df_cloud = analytics.flag_anomalies()
except Exception as e:
    st.error(f"Error loading telemetry data: {e}")
    df_cloud = pd.DataFrame()

if not df_cloud.empty:
    df_cloud["timestamp"] = pd.to_datetime(df_cloud["timestamp"])
    df_cloud = df_cloud[df_cloud["cloud_provider"].isin(selected_providers)]
    if start_date and end_date:
        s = pd.to_datetime(start_date)
        e = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        df_cloud = df_cloud[(df_cloud["timestamp"] >= s) & (df_cloud["timestamp"] <= e)]

# ─── KPI Row ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">System Performance KPIs</div>', unsafe_allow_html=True)

if not df_cloud.empty:
    avg_cpu       = df_cloud["cpu_usage"].mean()    if "cpu_usage"    in df_cloud.columns else 0.0
    avg_util      = df_cloud["utilization"].mean()  if "utilization"  in df_cloud.columns else 0.0
    anomaly_count = int(df_cloud["anomaly_flag"].sum()) if "anomaly_flag" in df_cloud.columns else 0
    avg_latency   = df_cloud["latency_ms"].mean()   if "latency_ms"   in df_cloud.columns else 0.0

    c1, c2, c3 = st.columns(3)
    with c1:
        components.kpi_card("Avg CPU Usage", f"{avg_cpu:.1f}%", f"Avg Utilisation: {avg_util:.1f}%")
    with c2:
        components.anomaly_badge(anomaly_count)
    with c3:
        components.kpi_card("Avg Latency", f"{avg_latency:.1f} ms", "System response time")
else:
    st.warning("⚠️ No telemetry data matches the current filters.")

st.divider()

# ─── Spend Breakdown Charts ───────────────────────────────────────────────────
st.markdown('<div class="section-header">Spend Breakdown</div>', unsafe_allow_html=True)
ch1, ch2 = st.columns(2)

with ch1:
    if not df_cloud.empty:
        prov_cost = df_cloud.groupby("cloud_provider", as_index=False)["cost"].sum()
        prov_cost = prov_cost.sort_values("cost", ascending=False)
        components.bar_chart(prov_cost, "cloud_provider", "cost", "Cost by Cloud Provider ($)")
    else:
        st.info("No provider cost data for the active filter scope.")

with ch2:
    if "GCP" in selected_providers:
        try:
            df_gcp = analytics.cost_by_gcp_service()
            if selected_service != "All Services":
                df_gcp = df_gcp[df_gcp["service_name"] == selected_service]
            if not df_gcp.empty:
                components.bar_chart(df_gcp, "service_name", "total_cost_usd", "GCP Service Cost ($)")
            else:
                st.info("No GCP service matches the selected filter.")
        except Exception as e:
            st.error(f"GCP service cost error: {e}")
    else:
        st.info("Select **GCP** in the provider filter to show GCP service-level cost.")

st.divider()

# ─── Usage vs Price Decomposition ────────────────────────────────────────────
st.markdown('<div class="section-header">Cost Variance Decomposition</div>', unsafe_allow_html=True)
st.caption("Identifies whether total cost changes were driven by consumption shifts (Usage-driven), pricing model changes (Price-driven), or neither (Stable).")

try:
    decomp = analytics.usage_vs_price_decomposition()
    if selected_service != "All Services":
        decomp = decomp[decomp["service_name"] == selected_service]

    if not decomp.empty:
        disp = decomp.rename(columns={"classification": "Cause"}).copy()
        for col in ["early_usage", "late_usage"]:
            disp[col] = disp[col].map("{:,.3f}".format)
        for col in ["early_price", "late_price"]:
            disp[col] = disp[col].map("${:,.5f}".format)
        disp = disp[["service_name", "early_usage", "late_usage", "early_price", "late_price", "Cause"]]

        def _cause_style(val):
            v = str(val).lower()
            if "usage" in v:   return "background:#1E3A5F;color:#93C5FD;font-weight:600;"
            if "price" in v:   return "background:#3B2B00;color:#FCD34D;font-weight:600;"
            if "stable" in v:  return "background:#064E3B;color:#6EE7B7;font-weight:600;"
            return ""

        st.dataframe(
            disp.style.map(_cause_style, subset=["Cause"]),
            use_container_width=True,
        )
        components.export_button(decomp, "cost_variance_decomposition.csv")
    else:
        st.info("No decomposition data for the current filter scope.")
except Exception as e:
    st.error(f"Decomposition error: {e}")

st.divider()

# ─── Target-Cost Correlation ──────────────────────────────────────────────────
st.markdown('<div class="section-header">Cost vs Scaling Target Correlation</div>', unsafe_allow_html=True)
st.caption(
    "Average observed cost grouped by the auto-scaling recommendation signal. "
    "This is a **proxy metric** derived from telemetry labels — "
    "it does not reflect direct deployment-triggered billing events."
)

try:
    corr = analytics.target_cost_correlation()
    if not corr.empty:
        disp_c = corr.copy()
        disp_c["avg_cost"] = disp_c["avg_cost"].map("${:,.4f}".format)
        st.dataframe(disp_c, use_container_width=True)
        components.export_button(corr, "target_cost_correlation.csv")
    else:
        st.info("No target-cost correlation data available.")
except Exception as e:
    st.error(f"Correlation error: {e}")
