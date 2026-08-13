import streamlit as st
from datetime import date

def date_range_filter():
    """
    Renders a date range selector in the sidebar.
    Returns (start_date, end_date) as datetime.date objects, or (None, None) if not selected.
    """
    st.sidebar.markdown("**Select Date Range**")
    dates = st.sidebar.date_input(
        "Date Range",
        value=[],
        label_visibility="collapsed"
    )
    if isinstance(dates, (tuple, list)):
        if len(dates) == 2:
            return dates[0], dates[1]
        elif len(dates) == 1:
            # Return the single date as both start and end to avoid None errors in downstream functions
            return dates[0], dates[0]
    return None, None

def provider_filter(options=["Azure", "AWS", "GCP"]):
    """
    Renders a multi-select filter for cloud providers in the sidebar.
    Returns the list of selected providers.
    """
    st.sidebar.markdown("**Select Cloud Provider**")
    selected = st.sidebar.multiselect(
        "Cloud Providers",
        options=options,
        default=options,
        label_visibility="collapsed"
    )
    return selected

def service_filter(options):
    """
    Renders a dropdown filter for services in the sidebar.
    Returns the selected service name, or "All Services" by default.
    """
    st.sidebar.markdown("**Select GCP Services**")
    clean_options = list(options) if options else []
    if "All Services" not in clean_options:
        clean_options.insert(0, "All Services")
        
    selected = st.sidebar.selectbox(
        "GCP Services",
        options=clean_options,
        index=0,
        label_visibility="collapsed"
    )
    return selected

if __name__ == "__main__":
    st.set_page_config(layout="wide")
    st.title("🔧 CostLens Filters Testing Sandbox")
    st.write("Interact with the sidebar filters to verify their return values in real-time.")
    
    # Execute sidebar filters
    start, end = date_range_filter()
    providers = provider_filter()
    service = service_filter(["Compute Engine", "Cloud Run", "BigQuery", "GKE"])
    
    st.write("---")
    st.subheader("📝 Dynamic Return Values")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("### Date Range")
        st.write(f"**Start Date**: `{start}` (Type: `{type(start).__name__}`)")
        st.write(f"**End Date**: `{end}` (Type: `{type(end).__name__}`)")
    with col2:
        st.info("### Cloud Providers")
        st.write(f"**Selected List**: `{providers}` (Type: `{type(providers).__name__}`)")
    with col3:
        st.info("### GCP Service")
        st.write(f"**Selected Value**: `'{service}'` (Type: `{type(service).__name__}`)")
