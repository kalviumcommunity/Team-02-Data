import streamlit as st
import sys
import os
import pandas as pd

# Ensure root folder is in python path for local imports
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import analytics
import components
import filters

# Page configuration
st.set_page_config(
    page_title="CostLens AI",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injected CSS for premium styling (Inter font and gradient titles)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="st-"] {
    font-family: 'Inter', sans-serif;
}

.main-title {
    font-size: 2.75rem;
    font-weight: 800;
    background: linear-gradient(90deg, #6366F1 0%, #10B981 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
}

.subtitle {
    font-size: 1.1rem;
    color: #94A3B8;
    margin-bottom: 2rem;
}

div[data-testid="stSidebar"] {
    background-color: #0F172A;
    border-right: 1px solid #1E293B;
}
</style>
""", unsafe_allow_html=True)

# 1. Fetch GCP service options dynamically from database
try:
    gcp_services_df = analytics.cost_by_gcp_service()
    gcp_services = sorted(gcp_services_df['service_name'].unique().tolist())
except Exception:
    gcp_services = []

# 2. Render sidebar filters
st.sidebar.markdown("<h2 style='color: #F8FAFC; font-weight: 700; margin-bottom: 1.5rem;'>Filter Scope</h2>", unsafe_allow_html=True)

selected_providers = filters.provider_filter()
start_date, end_date = filters.date_range_filter()
selected_service = filters.service_filter(gcp_services)

st.sidebar.markdown("---")
st.sidebar.caption("🔧 **Global Filters**: Filters adjusted here dynamically calculate the overview summary below.")

# Main Dashboard Welcome
st.markdown('<h1 class="main-title">CostLens AI</h1>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Multi-Dimensional Cloud Cost Intelligence & Root Cause Attribution</div>', unsafe_allow_html=True)

st.write("---")

st.markdown("""
### 🔍 Overview
**CostLens AI** is designed to solve a critical issue in cloud cost management: the inability of finance teams 
to attribute sudden cost spikes to specific engineering events (such as code releases or deployment scaling).
By correlating cloud infrastructure usage (CPU, memory, net IO) and deployment history against GCP billing datasets, 
this dashboard exposes the true drivers behind cloud infrastructure cost changes.
""")

# 3. Load & Calculate Real Summary Metrics
try:
    df_cloud = analytics.flag_anomalies()
except Exception:
    df_cloud = pd.DataFrame()

# Apply filters
if not df_cloud.empty:
    df_cloud['timestamp'] = pd.to_datetime(df_cloud['timestamp'])
    df_cloud = df_cloud[df_cloud['cloud_provider'].isin(selected_providers)]
    if start_date and end_date:
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        df_cloud = df_cloud[(df_cloud['timestamp'] >= start_dt) & (df_cloud['timestamp'] <= end_dt)]

# Calculate values
if not df_cloud.empty:
    total_spend = df_cloud['cost'].sum()
    anomaly_count = int(df_cloud['anomaly_flag'].sum())
else:
    total_spend = 0.0
    anomaly_count = 0

# Calculate Savings Potential
savings_potential = 0.0
if "GCP" in selected_providers:
    try:
        opt_df = analytics.optimisation_candidates()
        if selected_service != "All Services":
            opt_df = opt_df[opt_df['service_name'] == selected_service]
        savings_potential = float(opt_df['total_cost_usd'].sum())
    except Exception:
        pass

# Display Real Metrics
st.write("### 📊 Enterprise Summary")
col1, col2, col3 = st.columns(3)
with col1:
    components.kpi_card("Aggregated Multi-Cloud Spend", f"${total_spend:,.2f}", "Calculated from active filter scope")
with col2:
    components.anomaly_badge(anomaly_count)
with col3:
    components.kpi_card("Savings Potential", f"${savings_potential:,.2f}", "Under-utilized GCP services")

st.write("---")

# Quick Navigation Section
st.markdown("""
### 🚀 Navigation Guide
Use the sidebar options to explore specific dashboard views:
- **Executive View**: High-level spending trends, team-wise cost distribution, and cost projection forecasting.
- **Engineering View**: Resource utilization profiles, deployment metrics correlation, and price-vs-usage attribution.
- **FinOps View**: Idle resources detection, optimization candidates, and efficiency KPIs.
""")
