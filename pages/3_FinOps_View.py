import streamlit as st
import sys
import os
# Ensure root folder is in python path for components import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from components import kpi_card

st.set_page_config(layout="wide", page_title="FinOps View - CostLens AI")
st.title("💸 FinOps View")
st.write("---")
st.write("### 📊 Cost Optimization Recommendations & Savings (Dummy Data)")

col1, col2, col3 = st.columns(3)
with col1:
    kpi_card("Potential Monthly Savings", "$8,450.00", "+$420 vs Last Week")
with col2:
    kpi_card("Rightsizing Targets", "14 resources", "Ready to Action")
with col3:
    kpi_card("Average Unit Cost (GCP)", "$0.042 / core-hr", "-3.5% vs Target")

st.write("---")
st.info("💡 **Day 1 Placeholder**: This view is owned by your teammate and will focus on cost recommendations, idle resource alerts, and cost optimization tracking.")
