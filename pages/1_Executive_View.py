import streamlit as st
import sys
import os
# Ensure root folder is in python path for components import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from components import kpi_card

st.set_page_config(layout="wide", page_title="Executive View - CostLens AI")
st.title("💼 Executive View")
st.write("---")
st.write("### 📊 High-Level Financial Performance & Projections (Dummy Data)")

col1, col2, col3 = st.columns(3)
with col1:
    kpi_card("Total Multi-Cloud Spend", "$124,580.00", "+5.4% vs Last Month")
with col2:
    kpi_card("Budget Variance", "-2.4%", "Within Target")
with col3:
    kpi_card("Projected Month-End Spend", "$148,900.00", "+1.1% Variance")

st.write("---")
st.info("💡 **Day 1 Placeholder**: This view is owned by your teammate and will display long-term trends, team-wise distributions, and cost forecasting.")
