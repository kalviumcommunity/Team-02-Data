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

def anomaly_badge(count):
    """
    Renders a premium visual badge showing the number of flagged cost anomalies.
    """
    if count > 0:
        badge_style = f"""
        <div style="
            display: inline-flex;
            align-items: center;
            background-color: #7F1D1D;
            color: #F87171;
            border: 1px solid #991B1B;
            border-radius: 9999px;
            padding: 0.35rem 0.85rem;
            font-size: 0.875rem;
            font-weight: 600;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
            margin: 0.5rem 0;
        ">
            <span style="margin-right: 0.35rem;">⚠️</span> {count} Cost Anomalies Flagged
        </div>
        """
    else:
        badge_style = """
        <div style="
            display: inline-flex;
            align-items: center;
            background-color: #064E3B;
            color: #34D399;
            border: 1px solid #065F46;
            border-radius: 9999px;
            padding: 0.35rem 0.85rem;
            font-size: 0.875rem;
            font-weight: 600;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
            margin: 0.5rem 0;
        ">
            <span style="margin-right: 0.35rem;">✅</span> No Cost Anomalies Flagged
        </div>
        """
    st.markdown(badge_style, unsafe_allow_html=True)

def trend_chart(historical_df, projection_df, r_squared):
    """
    Renders a continuous line chart combining historical spend and projections.
    Includes an honest R^2 metric description as caption.
    """
    st.markdown("#### Cost Trends & Projections")
    
    # Standardize columns
    hist = historical_df.copy()
    proj = projection_df.copy()
    
    # Find column names dynamically to make it robust
    h_date_col = next((c for c in hist.columns if 'date' in c.lower()), hist.columns[0])
    h_cost_col = next((c for c in hist.columns if 'cost' in c.lower() or 'spend' in c.lower()), hist.columns[1])
    
    p_date_col = next((c for c in proj.columns if 'date' in c.lower()), proj.columns[0])
    p_cost_col = next((c for c in proj.columns if 'cost' in c.lower() or 'spend' in c.lower()), proj.columns[1])
    
    hist_cleaned = hist[[h_date_col, h_cost_col]].copy()
    hist_cleaned.columns = ['Date', 'Historical Cost ($)']
    hist_cleaned['Date'] = pd.to_datetime(hist_cleaned['Date'])
    
    proj_cleaned = proj[[p_date_col, p_cost_col]].copy()
    proj_cleaned.columns = ['Date', 'Projected Cost ($)']
    proj_cleaned['Date'] = pd.to_datetime(proj_cleaned['Date'])
    
    # Seamless connection: add last historical point to projection
    if not hist_cleaned.empty and not proj_cleaned.empty:
        last_hist_row = hist_cleaned.sort_values('Date').iloc[-1]
        conn_row = pd.DataFrame([{
            'Date': last_hist_row['Date'],
            'Projected Cost ($)': last_hist_row['Historical Cost ($)']
        }])
        proj_cleaned = pd.concat([conn_row, proj_cleaned], ignore_index=True)
        
    combined = pd.merge(hist_cleaned, proj_cleaned, on='Date', how='outer')
    combined = combined.sort_values('Date').set_index('Date')
    
    st.line_chart(combined)
    
    # Honest display of R^2 coefficient
    st.caption(
        f"📈 **Trend Model**: Simple linear regression projection. "
        f"**R² (Coefficient of Determination)** = `{r_squared:.4f}`. "
        f"A value close to 1 implies strong linear trend, whereas close to 0 indicates high variance and low predictive accuracy."
    )

if __name__ == "__main__":
    st.set_page_config(layout="wide", page_title="Component Testing Sandbox v2")
    st.title("🔧 CostLens Component Testing Sandbox v2")
    
    st.subheader("1. Anomaly Badges")
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        st.write("Anomalies > 0:")
        anomaly_badge(4)
    with col_b2:
        st.write("Anomalies = 0:")
        anomaly_badge(0)
        
    st.write("---")
    st.subheader("2. Historical + Projected Spend Chart")
    
    # Generate dummy historical data
    h_dates = pd.date_range(start="2026-08-01", periods=15)
    historical_data = pd.DataFrame({
        "date": h_dates,
        "daily_cost": [100, 105, 110, 108, 115, 120, 125, 122, 130, 135, 140, 138, 145, 150, 155]
    })
    
    # Generate dummy projection data
    p_dates = pd.date_range(start="2026-08-16", periods=7)
    projection_data = pd.DataFrame({
        "date": p_dates,
        "projected_cost": [158, 161, 164, 167, 170, 173, 176]
    })
    
    trend_chart(historical_data, projection_data, r_squared=0.9654)
