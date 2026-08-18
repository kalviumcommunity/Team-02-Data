import streamlit as st
import sys
import os
import pandas as pd

# Ensure root folder is in python path for local imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from components import kpi_card, line_chart, trend_chart, anomaly_badge
import analytics as aly

st.set_page_config(layout="wide", page_title="Executive View - CostLens AI")

# Injected CSS for premium styling (Inter font and gradient titles)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="st-"] {
    font-family: 'Inter', sans-serif;
}

.main-title {
    font-size: 2.5rem;
    font-weight: 800;
    background: linear-gradient(90deg, #6366F1 0%, #10B981 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
}

.subtitle {
    font-size: 1.0rem;
    color: #94A3B8;
    margin-bottom: 1.5rem;
}
</style>
""", unsafe_allow_html=True)

# Main Title & Subtitle
st.markdown('<h1 class="main-title">💼 Executive View</h1>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">High-Level Financial Performance, Anomalies, & Spend Projections</div>', unsafe_allow_html=True)
st.write("---")

# Cached data loaders
@st.cache_data
def cached_daily_cost_trend():
    return aly.daily_cost_trend()

@st.cache_data
def cached_cost_by_gcp_service():
    return aly.cost_by_gcp_service()

@st.cache_data
def cached_flag_anomalies():
    return aly.flag_anomalies()

@st.cache_data
def cached_project_trend():
    return aly.project_trend()

# Load Data
df_daily_trend = cached_daily_cost_trend()
df_gcp_services = cached_cost_by_gcp_service()
df_anomalies = cached_flag_anomalies()
df_projection, r_squared = cached_project_trend()

# Calculate KPI values
total_gcp_spend = float(df_gcp_services['total_cost_usd'].sum()) if not df_gcp_services.empty else 0.0
total_cloud_usage_spend = float(df_daily_trend['daily_cost'].sum()) if not df_daily_trend.empty else 0.0

# Count active anomalies
anomaly_count = int(df_anomalies['anomaly_flag'].sum()) if 'anomaly_flag' in df_anomalies.columns else 0

# UI Row 1: KPI Cards
col1, col2, col3 = st.columns(3)
with col1:
    kpi_card("Total GCP Billing Spend", f"${total_gcp_spend:,.2f}", "Overall historical period")
with col2:
    kpi_card("Active Anomalies Detected", f"{anomaly_count} Anomalies", "z-score threshold > 2.0")
with col3:
    kpi_card("Trend Model Fit (R²)", f"{r_squared:.4f}", "Degree-1 Polynomial Fit")

# Anomaly Badge Callout
anomaly_badge(anomaly_count)

st.write("---")

# Visual Charts Section
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    line_chart(df_daily_trend, x_col='date', y_col='daily_cost', title="Multi-Cloud Telemetry Daily Spend")

with col_chart2:
    trend_chart(df_daily_trend.rename(columns={'daily_cost': 'cost'}), df_projection, r_squared)
    # plain-English warning message if R^2 < 0.5
    if r_squared < 0.5:
        st.warning("⚠️ **Note**: Cost doesn't follow a strong linear trend in this data (R² is low). Use this projection with caution.")
