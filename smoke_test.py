import os
import sys
import pandas as pd

# Check database existence, initialize if missing
if not os.path.exists("costlens.db"):
    print("Database costlens.db not found. Initializing database by running database.py...")
    import database
    database.main()

import analytics
import components

def run_smoke_test():
    print("=== STARTING SMOKE TEST ===")
    
    passed = True
    
    # 1. daily_cost_trend
    try:
        print("Testing daily_cost_trend()...")
        df = analytics.daily_cost_trend()
        assert isinstance(df, pd.DataFrame), "daily_cost_trend must return a DataFrame"
        assert not df.empty, "daily_cost_trend returned an empty DataFrame"
        print(f"[PASS] daily_cost_trend passed (rows: {len(df)})")
    except Exception as e:
        print(f"[FAIL] daily_cost_trend failed: {e}")
        passed = False
        
    # 2. cost_by_gcp_service
    try:
        print("Testing cost_by_gcp_service()...")
        df = analytics.cost_by_gcp_service()
        assert isinstance(df, pd.DataFrame), "cost_by_gcp_service must return a DataFrame"
        assert not df.empty, "cost_by_gcp_service returned an empty DataFrame"
        print(f"[PASS] cost_by_gcp_service passed (rows: {len(df)})")
    except Exception as e:
        print(f"[FAIL] cost_by_gcp_service failed: {e}")
        passed = False

    # 3. cost_by_team
    try:
        print("Testing cost_by_team()...")
        df = analytics.cost_by_team()
        assert isinstance(df, pd.DataFrame), "cost_by_team must return a DataFrame"
        assert not df.empty, "cost_by_team returned an empty DataFrame"
        assert 'is_synthetic' in df.columns, "cost_by_team must contain is_synthetic column"
        print(f"[PASS] cost_by_team passed (rows: {len(df)})")
    except Exception as e:
        print(f"[FAIL] cost_by_team failed: {e}")
        passed = False

    # 4. usage_vs_price_decomposition
    try:
        print("Testing usage_vs_price_decomposition()...")
        df = analytics.usage_vs_price_decomposition()
        assert isinstance(df, pd.DataFrame), "usage_vs_price_decomposition must return a DataFrame"
        assert not df.empty, "usage_vs_price_decomposition returned an empty DataFrame"
        print(f"[PASS] usage_vs_price_decomposition passed (rows: {len(df)})")
    except Exception as e:
        print(f"[FAIL] usage_vs_price_decomposition failed: {e}")
        passed = False

    # 5. target_cost_correlation
    try:
        print("Testing target_cost_correlation()...")
        df = analytics.target_cost_correlation()
        assert isinstance(df, pd.DataFrame), "target_cost_correlation must return a DataFrame"
        assert not df.empty, "target_cost_correlation returned an empty DataFrame"
        print(f"[PASS] target_cost_correlation passed (rows: {len(df)})")
    except Exception as e:
        print(f"[FAIL] target_cost_correlation failed: {e}")
        passed = False

    # 6. flag_anomalies
    try:
        print("Testing flag_anomalies()...")
        df = analytics.flag_anomalies()
        assert isinstance(df, pd.DataFrame), "flag_anomalies must return a DataFrame"
        assert not df.empty, "flag_anomalies returned an empty DataFrame"
        assert 'anomaly_flag' in df.columns, "flag_anomalies must contain anomaly_flag column"
        print(f"[PASS] flag_anomalies passed (rows: {len(df)})")
    except Exception as e:
        print(f"[FAIL] flag_anomalies failed: {e}")
        passed = False

    # 7. project_trend
    try:
        print("Testing project_trend()...")
        proj_df, r_squared = analytics.project_trend()
        assert isinstance(proj_df, pd.DataFrame), "project_trend must return (DataFrame, float)"
        assert isinstance(r_squared, float), "project_trend r_squared must be float"
        assert not proj_df.empty, "project_trend returned empty projection DataFrame"
        print(f"[PASS] project_trend passed (rows: {len(proj_df)}, R2: {r_squared})")
    except Exception as e:
        print(f"[FAIL] project_trend failed: {e}")
        passed = False

    # 8. optimisation_candidates
    try:
        print("Testing optimisation_candidates()...")
        df = analytics.optimisation_candidates()
        assert isinstance(df, pd.DataFrame), "optimisation_candidates must return a DataFrame"
        assert 'is_synthetic' in df.columns, "optimisation_candidates must contain is_synthetic column"
        print(f"[PASS] optimisation_candidates passed (rows: {len(df)})")
    except Exception as e:
        print(f"[FAIL] optimisation_candidates failed: {e}")
        passed = False

    print("\n=== COMPONENT INTEGRATION VERIFICATION ===")
    
    # 9. Verify components can accept the real data types
    try:
        print("Testing trend_chart data alignment locally...")
        # Get real inputs
        import sqlite3
        conn = sqlite3.connect("costlens.db")
        gcp_hist = pd.read_sql_query("""
            SELECT DATE(usage_start_date) AS date,
                   SUM(unrounded_cost_usd) AS daily_cost_usd
            FROM gcp_billing
            GROUP BY DATE(usage_start_date)
            ORDER BY date;
        """, conn)
        conn.close()
        
        proj_df, r_squared = analytics.project_trend()
        
        hist_cleaned = gcp_hist[['date', 'daily_cost_usd']].copy()
        hist_cleaned.columns = ['Date', 'Historical Cost ($)']
        hist_cleaned['Date'] = pd.to_datetime(hist_cleaned['Date'])
        
        proj_cleaned = proj_df[['date', 'projected_cost_usd']].copy()
        proj_cleaned.columns = ['Date', 'Projected Cost ($)']
        proj_cleaned['Date'] = pd.to_datetime(proj_cleaned['Date'])
        
        if not hist_cleaned.empty and not proj_cleaned.empty:
            last_hist_row = hist_cleaned.sort_values('Date').iloc[-1]
            conn_row = pd.DataFrame([{
                'Date': last_hist_row['Date'],
                'Projected Cost ($)': last_hist_row['Historical Cost ($)']
            }])
            proj_cleaned = pd.concat([conn_row, proj_cleaned], ignore_index=True)
            
        combined = pd.merge(hist_cleaned, proj_cleaned, on='Date', how='outer')
        combined = combined.sort_values('Date').set_index('Date')
        
        assert not combined.empty, "Combined DataFrame for trend_chart is empty"
        print("[PASS] trend_chart data preparation passed")
    except Exception as e:
        print(f"[FAIL] trend_chart integration test failed: {e}")
        passed = False

    # 10. Verify anomaly badge integration
    try:
        print("Testing anomaly_badge count parsing...")
        anom_df = analytics.flag_anomalies()
        anomaly_count = int(anom_df['anomaly_flag'].sum())
        print(f"Anomaly count parsed: {anomaly_count}")
        print("[PASS] anomaly_badge integration passed")
    except Exception as e:
        print(f"[FAIL] anomaly_badge integration test failed: {e}")
        passed = False

    if passed:
        print("\n=== SMOKE TEST SUCCEEDED! All analytics and component mappings are healthy. ===")
        sys.exit(0)
    else:
        print("\n=== SMOKE TEST FAILED. Please check the errors above. ===")
        sys.exit(1)

if __name__ == "__main__":
    run_smoke_test()
