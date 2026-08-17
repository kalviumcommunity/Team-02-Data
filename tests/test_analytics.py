import pytest
import pandas as pd
from analytics import (
    daily_cost_trend,
    cost_by_gcp_service,
    cost_by_team,
    usage_vs_price_decomposition,
    target_cost_correlation,
    flag_anomalies,
    project_trend,
    optimisation_candidates,
)

def test_daily_cost_trend():
    df = daily_cost_trend()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty

def test_cost_by_gcp_service():
    df = cost_by_gcp_service()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty

def test_cost_by_team():
    df = cost_by_team()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty

def test_usage_vs_price_decomposition():
    df = usage_vs_price_decomposition()
    assert isinstance(df, pd.DataFrame)
    # May be empty if data insufficient, but should return DataFrame

def test_target_cost_correlation():
    df = target_cost_correlation()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty

def test_flag_anomalies():
    df = flag_anomalies()
    assert isinstance(df, pd.DataFrame)
    assert 'anomaly_flag' in df.columns

def test_project_trend():
    proj_df, r2 = project_trend()
    assert isinstance(proj_df, pd.DataFrame)
    assert isinstance(r2, float)

def test_optimisation_candidates():
    df = optimisation_candidates()
    assert isinstance(df, pd.DataFrame)
    # May be empty if no low utilisation services
