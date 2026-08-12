import streamlit as st
import sys
import os
# Ensure root folder is in python path for components import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from components import kpi_card

st.set_page_config(layout="wide", page_title="Engineering View - CostLens AI")
st.title("🛠️ Engineering View")
st.write("---")
st.write("### 📊 Resource Utilization & Cost Attribution (Dummy Data)")

col1, col2, col3 = st.columns(3)
with col1:
    kpi_card("Avg CPU Utilization", "34.2%", "-1.5% vs Last Week")
with col2:
    kpi_card("Idle Instances", "8 instances", "+2 in 24h")
with col3:
    kpi_card("Anomalies Logged", "5 events", "Requires Attention")

st.write("---")
st.info("💡 **Day 1 Placeholder**: This view is owned by you and will focus on resource metrics, deployment history correlation, and price-vs-usage attribution.")
