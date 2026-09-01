import streamlit as st
import pandas as pd

# ─────────────────────────────────────────────────────────────────────────────
# Shared global CSS injected once from this module (harmless to re-inject per page)
# ─────────────────────────────────────────────────────────────────────────────
GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="st-"] {
    font-family: 'Inter', sans-serif !important;
}

/* Metric card base */
.cl-card {
    background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 16px;
    padding: 1.4rem 1.5rem;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.05);
    margin: 0.4rem 0;
    transition: box-shadow 0.2s ease;
}

/* Sidebar background */
div[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0B1120 0%, #0F172A 100%) !important;
    border-right: 1px solid #1E293B !important;
}

/* Sidebar nav items */
section[data-testid="stSidebar"] a {
    color: #94A3B8 !important;
    font-weight: 500;
}

section[data-testid="stSidebar"] a:hover {
    color: #F8FAFC !important;
}

/* Divider line */
hr { border-color: #1E293B !important; }

/* Dataframe tables */
.stDataFrame { border-radius: 12px; overflow: hidden; }

/* Caption styling */
.stCaption { color: #64748B; font-size: 0.8rem; }
</style>
"""

def inject_global_css():
    """Inject the shared global CSS styles. Call at the top of each page."""
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def kpi_card(label, value, delta=None):
    """
    Renders a premium visual KPI card with optional delta tracking.
    Delta strings beginning with '-' are shown in red, others in green.
    """
    delta_html = ""
    if delta is not None:
        delta_str = str(delta)
        is_negative = delta_str.startswith("-") or (isinstance(delta, (int, float)) and delta < 0)
        is_neutral = delta_str in ("0", "0%", "")

        if is_negative:
            color = "#EF4444"
            arrow = "▼"
        elif is_neutral:
            color = "#64748B"
            arrow = "—"
        else:
            color = "#10B981"
            arrow = "▲"
            if not delta_str.startswith("+"):
                delta_str = f"+{delta_str}"

        delta_html = (
            f'<div style="font-size:0.82rem;font-weight:600;color:{color};margin-top:0.35rem;">'
            f'{arrow}&nbsp;{delta_str}</div>'
        )

    html = f"""
    <div class="cl-card">
        <div style="font-size:0.72rem;color:#64748B;font-weight:600;
                    text-transform:uppercase;letter-spacing:0.08em;">{label}</div>
        <div style="font-size:1.9rem;color:#F8FAFC;font-weight:800;
                    margin-top:0.3rem;line-height:1.15;letter-spacing:-0.02em;">{value}</div>
        {delta_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def line_chart(df, x_col, y_col, title):
    """Renders a titled line chart."""
    st.markdown(
        f'<div style="font-size:1rem;font-weight:600;color:#CBD5E1;margin-bottom:0.25rem;">{title}</div>',
        unsafe_allow_html=True
    )
    chart_data = df[[x_col, y_col]].copy().set_index(x_col)
    st.line_chart(chart_data, use_container_width=True)


def bar_chart(df, x_col, y_col, title):
    """Renders a titled bar chart."""
    st.markdown(
        f'<div style="font-size:1rem;font-weight:600;color:#CBD5E1;margin-bottom:0.25rem;">{title}</div>',
        unsafe_allow_html=True
    )
    chart_data = df[[x_col, y_col]].copy().set_index(x_col)
    st.bar_chart(chart_data, use_container_width=True)


def export_button(df, filename):
    """Renders a styled CSV export download button."""
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥  Export as CSV",
        data=csv,
        file_name=filename,
        mime="text/csv",
        key=f"dl_{filename}_{df.shape[0]}",
    )


def anomaly_badge(count):
    """
    Renders a pill badge — red/orange if anomalies exist, green if clean.
    """
    if count > 0:
        badge = f"""
        <div style="display:inline-flex;align-items:center;gap:0.45rem;
                    background:#7F1D1D;color:#FCA5A5;
                    border:1px solid #991B1B;border-radius:9999px;
                    padding:0.4rem 1rem;font-size:0.85rem;font-weight:600;
                    box-shadow:0 4px 12px rgba(239,68,68,0.2);margin:0.5rem 0;">
            ⚠️&nbsp;{count} Cost Anomalies Flagged
        </div>"""
    else:
        badge = """
        <div style="display:inline-flex;align-items:center;gap:0.45rem;
                    background:#064E3B;color:#6EE7B7;
                    border:1px solid #065F46;border-radius:9999px;
                    padding:0.4rem 1rem;font-size:0.85rem;font-weight:600;
                    box-shadow:0 4px 12px rgba(16,185,129,0.15);margin:0.5rem 0;">
            ✅&nbsp;No Cost Anomalies Detected
        </div>"""
    st.markdown(badge, unsafe_allow_html=True)


def trend_chart(historical_df, projection_df, r_squared):
    """
    Renders a continuous line chart combining historical spend and projections.
    Seamlessly bridges the two series and honestly shows the R² value.
    """
    st.markdown(
        '<div style="font-size:1rem;font-weight:600;color:#CBD5E1;margin-bottom:0.25rem;">'
        'Cost Trend &amp; 7-Day Projection</div>',
        unsafe_allow_html=True
    )

    hist = historical_df.copy()
    proj = projection_df.copy()

    # Detect column names dynamically
    h_date  = next((c for c in hist.columns if "date" in c.lower()), hist.columns[0])
    h_cost  = next((c for c in hist.columns if "cost" in c.lower() or "spend" in c.lower()), hist.columns[1])
    p_date  = next((c for c in proj.columns if "date" in c.lower()), proj.columns[0])
    p_cost  = next((c for c in proj.columns if "cost" in c.lower() or "spend" in c.lower()), proj.columns[1])

    hist_c = hist[[h_date, h_cost]].copy()
    hist_c.columns = ["Date", "Historical Cost ($)"]
    hist_c["Date"] = pd.to_datetime(hist_c["Date"])

    proj_c = proj[[p_date, p_cost]].copy()
    proj_c.columns = ["Date", "Projected Cost ($)"]
    proj_c["Date"] = pd.to_datetime(proj_c["Date"])

    # Bridge gap — last historical point = first projected point
    if not hist_c.empty and not proj_c.empty:
        bridge = hist_c.sort_values("Date").iloc[[-1]].copy()
        bridge = bridge.rename(columns={"Historical Cost ($)": "Projected Cost ($)"})[["Date", "Projected Cost ($)"]]
        proj_c = pd.concat([bridge, proj_c], ignore_index=True)

    combined = (
        pd.merge(hist_c, proj_c, on="Date", how="outer")
        .sort_values("Date")
        .set_index("Date")
    )
    st.line_chart(combined, use_container_width=True)

    r2_color = "#10B981" if r_squared >= 0.5 else "#F59E0B"
    quality  = "Strong" if r_squared >= 0.7 else ("Moderate" if r_squared >= 0.4 else "Weak")
    st.markdown(
        f'<div style="font-size:0.78rem;color:#64748B;margin-top:0.3rem;">'
        f'📈 Linear regression fit &nbsp;|&nbsp; '
        f'R² = <span style="color:{r2_color};font-weight:700;">{r_squared:.4f}</span> '
        f'({quality} fit) &nbsp;— projection accuracy may vary.</div>',
        unsafe_allow_html=True
    )


# ─── Sandbox Testing Block ────────────────────────────────────────────────────
if __name__ == "__main__":
    st.set_page_config(layout="wide", page_title="Component Sandbox")
    inject_global_css()
    st.title("🔧 CostLens Component Sandbox")

    st.subheader("1. KPI Cards")
    c1, c2, c3 = st.columns(3)
    with c1: kpi_card("Total Spend", "$42,810.55", "+8.3% vs last month")
    with c2: kpi_card("Active Instances", "47", "-2 instances")
    with c3: kpi_card("Avg Latency", "128.4 ms", "0%")

    st.write("---")
    st.subheader("2. Anomaly Badges")
    b1, b2 = st.columns(2)
    with b1: anomaly_badge(5)
    with b2: anomaly_badge(0)

    st.write("---")
    st.subheader("3. Charts")
    dates = pd.date_range("2026-08-01", periods=12)
    dummy = pd.DataFrame({"Date": dates.strftime("%Y-%m-%d"),
                          "Cost": [100+i*8 for i in range(12)],
                          "Usage": [50+i*3 for i in range(12)]})
    ch1, ch2 = st.columns(2)
    with ch1: line_chart(dummy, "Date", "Cost", "Daily Spend ($)")
    with ch2: bar_chart(dummy, "Date", "Usage", "vCPU Hours")

    st.write("---")
    st.subheader("4. Export Button")
    export_button(dummy, "sandbox_test.csv")

    st.write("---")
    st.subheader("5. Trend + Projection Chart")
    proj_dates = pd.date_range("2026-08-13", periods=7)
    proj = pd.DataFrame({"date": proj_dates, "projected_cost": [196+i*6 for i in range(7)]})
    trend_chart(dummy.rename(columns={"Date": "date", "Cost": "cost"}), proj, 0.71)
