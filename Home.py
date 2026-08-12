import streamlit as st
from components import kpi_card

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

# Sidebar Filter Skeletons
st.sidebar.markdown("<h2 style='color: #F8FAFC; font-weight: 700; margin-bottom: 1.5rem;'>Filter Scope</h2>", unsafe_allow_html=True)

st.sidebar.markdown("**Select Cloud Provider**")
cloud_providers = st.sidebar.multiselect(
    "Cloud Providers",
    options=["AWS", "Azure", "GCP"],
    default=["AWS", "Azure", "GCP"],
    label_visibility="collapsed"
)

st.sidebar.markdown("**Select Date Range**")
date_range = st.sidebar.date_input(
    "Date Range",
    value=[],
    label_visibility="collapsed"
)

st.sidebar.markdown("**Select GCP Services**")
gcp_services = st.sidebar.multiselect(
    "GCP Services",
    options=["Compute Engine", "Cloud Storage", "BigQuery", "Cloud Run", "Google Kubernetes Engine"],
    default=[],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Day 1 Skeleton**: Filters shown above are mock controls to demonstrate dashboard layout layout.")

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

# High-Level Metrics Row (Dummy Data)
st.write("### 📊 Enterprise Summary (Dummy Data)")
col1, col2, col3 = st.columns(3)
with col1:
    kpi_card("Month-to-Date Spend", "$45,210.89", "+4.2% vs Last Month")
with col2:
    kpi_card("Active Anomalies", "3 Detected", "+1 Spike Today")
with col3:
    kpi_card("Savings Potential", "$8,450.00 / mo", "12 Active Recommendations")

st.write("---")

# Quick Navigation Section
st.markdown("""
### 🚀 Navigation Guide
Use the sidebar options to explore specific dashboard views:
- **Executive View**: High-level spending trends, team-wise cost distribution, and cost projection forecasting.
- **Engineering View**: Resource utilization profiles, deployment metrics correlation, and price-vs-usage attribution.
- **FinOps View**: Idle resources detection, optimization candidates, and efficiency KPIs.
""")
