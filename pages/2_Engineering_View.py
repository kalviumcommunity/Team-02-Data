import streamlit as st
import sys
import os
import pandas as pd

# Ensure root folder is in python path for local imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import analytics
import components
import filters

# Set page config
st.set_page_config(layout="wide", page_title="Engineering View - CostLens AI")

# Custom styles
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="st-"] {
    font-family: 'Inter', sans-serif;
}

.main-title {
    font-size: 2.5rem;
    font-weight: 800;
    color: #F8FAFC;
    margin-bottom: 0.2rem;
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

# Run filters from filters.py
selected_providers = filters.provider_filter()
start_date, end_date = filters.date_range_filter()
selected_service = filters.service_filter(gcp_services)

st.sidebar.markdown("---")
st.sidebar.caption("🔧 **Engineering Filters**: These inputs filter the multi-cloud and GCP service metrics in real-time.")

# Main content
st.markdown('<h1 class="main-title">🛠️ Engineering View</h1>', unsafe_allow_html=True)
st.markdown("<p style='color: #94A3B8; margin-bottom: 2rem;'>Resource Utilization Profiles, Deployment History, and Price-vs-Usage Root Cause Analysis</p>", unsafe_allow_html=True)
st.write("---")

# 3. Load & Filter Data
# Fetch telemetry data
try:
    df_cloud = analytics.flag_anomalies()
except Exception as e:
    st.error(f"Error loading cloud telemetry data: {e}")
    df_cloud = pd.DataFrame()

if not df_cloud.empty:
    df_cloud['timestamp'] = pd.to_datetime(df_cloud['timestamp'])
    # Apply provider filter
    df_cloud = df_cloud[df_cloud['cloud_provider'].isin(selected_providers)]
    # Apply date filter
    if start_date and end_date:
        start_dt = pd.to_datetime(start_date)
        # End date inclusive of full day
        end_dt = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        df_cloud = df_cloud[(df_cloud['timestamp'] >= start_dt) & (df_cloud['timestamp'] <= end_dt)]

# 4. KPI Cards Row
st.subheader("⚙️ System Performance KPIs")
if not df_cloud.empty:
    # Derive KPIs
    avg_cpu = df_cloud['cpu_usage'].mean() if 'cpu_usage' in df_cloud.columns else 0.0
    avg_util = df_cloud['utilization'].mean() if 'utilization' in df_cloud.columns else 0.0
    anomalies_count = int(df_cloud['anomaly_flag'].sum()) if 'anomaly_flag' in df_cloud.columns else 0
    avg_latency = df_cloud['latency_ms'].mean() if 'latency_ms' in df_cloud.columns else 0.0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        components.kpi_card("Average CPU Usage", f"{avg_cpu:.1f}%", f"Overall Util: {avg_util:.1f}%")
    with col2:
        # Render anomaly badge using components.py
        components.anomaly_badge(anomalies_count)
    with col3:
        components.kpi_card("Average Latency", f"{avg_latency:.1f} ms", "System Response Time")
else:
    st.warning("No telemetry data matches the active filters.")

st.write("---")

# 5. Visual Cost Charts Row
st.subheader("📊 Spend Breakdown")
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    # Cost by Cloud Provider (Derived from telemetry data)
    if not df_cloud.empty:
        provider_cost = df_cloud.groupby('cloud_provider', as_index=False)['cost'].sum()
        components.bar_chart(provider_cost, 'cloud_provider', 'cost', "Cost by Cloud Provider ($)")
    else:
        st.info("No cloud provider cost data available for the active filters.")

with chart_col2:
    # Cost by GCP Service
    if "GCP" in selected_providers:
        try:
            df_gcp_cost = analytics.cost_by_gcp_service()
            if selected_service != "All Services":
                df_gcp_cost = df_gcp_cost[df_gcp_cost['service_name'] == selected_service]
            
            if not df_gcp_cost.empty:
                components.bar_chart(df_gcp_cost, 'service_name', 'total_cost_usd', "GCP Service Cost ($)")
            else:
                st.info("No GCP service cost matches the selected service filter.")
        except Exception as e:
            st.error(f"Error loading GCP service costs: {e}")
    else:
        st.info("Select 'GCP' in the provider list to display GCP Service Cost breakdown.")

st.write("---")

# 6. Usage vs Price Decomposition
st.subheader("🔄 Cost Variance Decomposition")
st.write("Analyzes price changes vs consumption shifts to identify why a service's total cost changed.")

try:
    decomp_df = analytics.usage_vs_price_decomposition()
    if selected_service != "All Services":
        decomp_df = decomp_df[decomp_df['service_name'] == selected_service]
        
    if not decomp_df.empty:
        # Rename classification to Cause for display
        decomp_disp = decomp_df.rename(columns={'classification': 'Cause'})
        
        # Format metrics for clean representation
        for col in ['early_usage', 'late_usage']:
            decomp_disp[col] = decomp_disp[col].map('{:,.2f}'.format)
        for col in ['early_price', 'late_price']:
            decomp_disp[col] = decomp_disp[col].map('${:,.4f}'.format)
            
        # Reorder columns for logical reading
        cols_order = ['service_name', 'early_usage', 'late_usage', 'early_price', 'late_price', 'Cause']
        decomp_disp = decomp_disp[cols_order]
        
        # Apply CSS styling to Cause column cells
        def style_cause_cell(val):
            val_str = str(val).lower()
            if 'usage' in val_str:
                return 'background-color: #1E293B; color: #38BDF8; font-weight: bold; border-radius: 4px;'
            elif 'price' in val_str:
                return 'background-color: #1E293B; color: #F59E0B; font-weight: bold; border-radius: 4px;'
            elif 'stable' in val_str:
                return 'background-color: #1E293B; color: #10B981; font-weight: bold; border-radius: 4px;'
            return ''
            
        styled_decomp = decomp_disp.style.map(style_cause_cell, subset=['Cause'])
        st.dataframe(styled_decomp, use_container_width=True)
        
        # Export Button
        components.export_button(decomp_df, "usage_vs_price_decomposition.csv")
    else:
        st.info("No decomposition metrics match the current filters.")
except Exception as e:
    st.error(f"Error executing usage vs price decomposition: {e}")

st.write("---")

# 7. Target Cost Correlation
st.subheader("🎯 Cost vs Target Action Correlation")
st.write("Correlates telemetry metrics with scaling recommendations to gauge financial impact of automated actions.")

try:
    corr_df = analytics.target_cost_correlation()
    if not corr_df.empty:
        # Format average cost
        corr_disp = corr_df.copy()
        corr_disp['avg_cost'] = corr_disp['avg_cost'].map('${:,.2f}'.format)
        
        st.dataframe(corr_disp, use_container_width=True)
        st.caption("⚠️ **Disclaimer**: The cost correlation above is derived from telemetry proxy signals and resource cost allocations. It does not represent direct billing API logs of deployment-triggered changes.")
        
        # Export Button
        components.export_button(corr_df, "target_cost_correlation.csv")
    else:
        st.info("No target cost correlation data available.")
except Exception as e:
    st.error(f"Error loading target cost correlations: {e}")
