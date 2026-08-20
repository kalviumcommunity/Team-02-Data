import streamlit as st
import sys
import os
import pandas as pd

# Ensure root folder is in python path for local imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from components import kpi_card, bar_chart, export_button
import analytics as aly

st.set_page_config(layout="wide", page_title="FinOps View - CostLens AI")

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
    background: linear-gradient(90deg, #EC4899 0%, #8B5CF6 100%);
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
st.markdown('<h1 class="main-title">💸 FinOps View</h1>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Cost Optimization Recommendations, Idle Resource Detection, & Team Financial Governance</div>', unsafe_allow_html=True)
st.write("---")

# Prominent Disclaimer Callout
st.warning(
    "⚠️ **Disclaimer**: Team assignments are illustrative — no public dataset provides real engineering ownership data. "
    "Costs shown are real; team labels are synthetic."
)

st.write("")

# Cached data loaders
@st.cache_data
def cached_cost_by_team():
    return aly.cost_by_team()

@st.cache_data
def cached_optimisation_candidates():
    # Load with default 50.0 CPU threshold
    return aly.optimisation_candidates(utilisation_threshold=50.0)

# Load Data
df_team_cost = cached_cost_by_team()
df_opt_candidates = cached_optimisation_candidates()

# Calculate KPI values
total_optimization_saving_usd = float(df_opt_candidates['total_cost_usd'].sum()) if not df_opt_candidates.empty else 0.0
candidate_count = len(df_opt_candidates)

# UI Row 1: KPI Cards
col1, col2, col3 = st.columns(3)
with col1:
    kpi_card("Optimization Candidates", f"{candidate_count} Services", "CPU average under 50%")
with col2:
    kpi_card("Potential Savings Scope", f"${total_optimization_saving_usd:,.2f}", "Total cost of under-utilized services")
with col3:
    # Get total cost scope from team spend sum
    total_gcp_spend = float(df_team_cost['team_total_cost_usd'].sum()) if not df_team_cost.empty else 0.0
    kpi_card("Total GCP Cost Managed", f"${total_gcp_spend:,.2f}", "All synthetic teams combined")

st.write("---")

# UI Row 2: Team Cost Share Charts & Ranked Table
col_team1, col_team2 = st.columns(2)

with col_team1:
    st.subheader("👥 Cost Attributed by Team")
    # Display team cost ranked table
    if not df_team_cost.empty:
        # Format team_total_cost_usd columns for display
        df_team_disp = df_team_cost.copy()
        df_team_disp['team_total_cost_usd'] = df_team_disp['team_total_cost_usd'].map('${:,.2f}'.format)
        st.dataframe(df_team_disp, use_container_width=True)
        
        # Export Button
        export_button(df_team_cost, "cost_by_team.csv")
    else:
        st.info("No team cost attribution data available.")

with col_team2:
    if not df_team_cost.empty:
        bar_chart(df_team_cost, 'team_name', 'team_total_cost_usd', "Spend Contribution per Team ($)")
    else:
        st.info("No cost chart available due to missing team data.")

st.write("---")

# UI Row 3: Optimisation Candidates
st.subheader("💡 Under-Utilized GCP Services (CPU Utilization < 50%)")
st.write("The services listed below run at sub-50% CPU capacity on average, suggesting right-sizing opportunities.")

if not df_opt_candidates.empty:
    df_opt_disp = df_opt_candidates.copy()
    # Format CPU percent and total cost
    df_opt_disp['avg_cpu_util_pct'] = df_opt_disp['avg_cpu_util_pct'].map('{:.2f}%'.format)
    df_opt_disp['total_cost_usd'] = df_opt_disp['total_cost_usd'].map('${:,.2f}'.format)
    
    st.dataframe(df_opt_disp, use_container_width=True)
    
    # Export Button
    export_button(df_opt_candidates, "optimization_candidates.csv")
else:
    st.success("🎉 No GCP services currently fall under the 50% CPU utilization threshold!")
