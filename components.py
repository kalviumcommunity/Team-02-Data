import streamlit as st
import pandas as pd

def kpi_card(label, value, delta=None):
    """
    Renders a premium visual KPI card with optional delta tracking.
    """
    delta_html = ""
    if delta is not None:
        delta_str = str(delta)
        is_negative = delta_str.startswith("-") or (isinstance(delta, (int, float)) and delta < 0)
        is_neutral = delta_str == "0" or delta_str == "0%" or delta_str == ""
        
        if is_negative:
            color = "#EF4444"  # red-500
            arrow = "▼"
        elif is_neutral:
            color = "#94A3B8"  # slate-400
            arrow = ""
        else:
            color = "#10B981"  # emerald-500
            arrow = "▲"
            if not delta_str.startswith("+"):
                delta_str = f"+{delta_str}"
                
        delta_html = f'<div style="font-size: 0.9rem; font-weight: 600; color: {color}; margin-top: 0.2rem;">{arrow} {delta_str}</div>'

    card_style = """
    <div style="
        background-color: #0F172A; 
        border: 1px solid #1E293B; 
        border-radius: 12px; 
        padding: 1.25rem; 
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
        margin: 0.5rem 0;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    ">
        <div style="font-size: 0.875rem; color: #64748B; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em;">{label}</div>
        <div style="font-size: 1.75rem; color: #F8FAFC; font-weight: 700; margin-top: 0.25rem; line-height: 1.2;">{value}</div>
        {delta_html}
    </div>
    """
    st.markdown(card_style.format(label=label, value=value, delta_html=delta_html), unsafe_allow_html=True)

def line_chart(df, x_col, y_col, title):
    """
    Renders a line chart for the given DataFrame.
    """
    st.markdown(f"#### {title}")
    chart_data = df[[x_col, y_col]].copy()
    chart_data = chart_data.set_index(x_col)
    st.line_chart(chart_data)

def bar_chart(df, x_col, y_col, title):
    """
    Renders a bar chart for the given DataFrame.
    """
    st.markdown(f"#### {title}")
    chart_data = df[[x_col, y_col]].copy()
    chart_data = chart_data.set_index(x_col)
    st.bar_chart(chart_data)

def export_button(df, filename):
    """
    Provides a download button to export the DataFrame as a CSV.
    """
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export Data as CSV",
        data=csv,
        file_name=filename,
        mime='text/csv',
        key=f"export_{filename}_{df.shape[0]}"
    )

if __name__ == "__main__":
    st.set_page_config(layout="wide", page_title="Component Testing")
    st.title("🔧 CostLens Component Testing Sandbox")
    st.write("Testing visual aesthetics and responsiveness of reusable widgets.")
    
    st.subheader("1. KPI Cards")
    col1, col2, col3 = st.columns(3)
    with col1:
        kpi_card("Total Cost (MTD)", "$12,450.80", "+12.4% vs last month")
    with col2:
        kpi_card("Active Instances", "42", "-3 instances")
    with col3:
        kpi_card("Storage Capacity", "1.2 TB", "0%")
        
    st.write("---")
    st.subheader("2. Visual Chart Widgets")
    
    # Generate dummy data
    dates = pd.date_range(start="2026-08-01", periods=10)
    dummy_df = pd.DataFrame({
        "Date": dates.strftime("%Y-%m-%d"),
        "Cost": [120, 150, 140, 180, 210, 190, 220, 250, 240, 270],
        "Usage": [50, 55, 52, 60, 68, 62, 70, 75, 72, 80]
    })
    
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        line_chart(dummy_df, "Date", "Cost", "Daily Infrastructure Spend ($)")
    with col_chart2:
        bar_chart(dummy_df, "Date", "Usage", "Compute Usage (vCPU Hours)")
        
    st.write("---")
    st.subheader("3. Data Exports")
    export_button(dummy_df, "cost_components_dummy.csv")
