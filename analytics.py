# analytics.py
"""Analytics Engine for CostLens AI

This module provides a collection of pure‑Python functions that query the
SQLite database ``costlens.db`` and compute various cost, usage, and optimisation
metrics required by the Streamlit dashboard.

All calculations use only the allowed stack: pandas, numpy, and sqlite3.
No machine‑learning libraries are imported.
"""

import sqlite3
from contextlib import contextmanager
from typing import Tuple

import numpy as np
import pandas as pd

import logging

# Configure module‑level logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('analytics.log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(handler)

DB_PATH = "costlens.db"

@contextmanager
def get_connection(read_only: bool = True):
    """Yield a SQLite connection.

    Args:
        read_only: If True, opens the database in read‑only mode to prevent
            accidental writes during analytics calculations.
    """
    uri = f"file:{DB_PATH}?mode={'ro' if read_only else 'rw'}"
    conn = sqlite3.connect(uri, uri=True)
    try:
        yield conn
    finally:
        conn.close()


def daily_cost_trend() -> pd.DataFrame:
    """Return a DataFrame with daily total cost from the ``cloud_usage`` table.

    The result has two columns: ``date`` (YYYY‑MM‑DD) and ``daily_cost``.
    """
    try:
        query = """
            SELECT DATE(timestamp) AS date, SUM(cost) AS daily_cost
            FROM cloud_usage
            GROUP BY DATE(timestamp)
            ORDER BY date;
        """
        with get_connection() as conn:
            df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        logger.error("Error in daily_cost_trend: %s", e)
        raise


def cost_by_gcp_service() -> pd.DataFrame:
    """Cost totals per GCP service from the ``gcp_billing`` table.

    Returns columns ``service_name`` and ``total_cost_usd``.
    """
    try:
        query = """
            SELECT service_name, SUM(unrounded_cost_usd) AS total_cost_usd
            FROM gcp_billing
            GROUP BY service_name
            ORDER BY total_cost_usd DESC;
        """
        with get_connection() as conn:
            df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        logger.error("Error in cost_by_gcp_service: %s", e)
        raise


def cost_by_team() -> pd.DataFrame:
    """Aggregate cost per synthetic team.

    Joins ``gcp_billing`` with ``team_ownership_gcp`` on ``service_name``.
    Returns ``team_name`` and ``team_total_cost_usd``.
    """
    try:
        query = """
            SELECT t.team_name,
                   SUM(b.unrounded_cost_usd) AS team_total_cost_usd,
                   MAX(t.is_synthetic) AS is_synthetic
            FROM gcp_billing b
            JOIN team_ownership_gcp t ON b.service_name = t.service_name
            GROUP BY t.team_name
            ORDER BY team_total_cost_usd DESC;
        """
        with get_connection() as conn:
            df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        logger.error("Error in cost_by_team: %s", e)
        raise


def usage_vs_price_decomposition() -> pd.DataFrame:
    """Decompose cost changes into usage-driven, price-driven, both, or stable.

    For each GCP service the dataset is split at the median ``usage_start_date``
    into an early and a late half.  Average ``usage_quantity`` and
    ``cost_per_quantity_usd`` are computed for each half.  The percentage change
    between the halves determines the classification.
    """
    try:
        # Load full billing table
        with get_connection() as conn:
            df = pd.read_sql_query("SELECT * FROM gcp_billing", conn)

        # Ensure proper date type
        df["usage_start_date"] = pd.to_datetime(df["usage_start_date"])
        median_date = df["usage_start_date"].median()

        def classify(row):
            usage_change = (row["late_usage"] - row["early_usage"]) / row["early_usage"]
            price_change = (row["late_price"] - row["early_price"]) / row["early_price"]
            thresh = 0.05
            usage_sig = abs(usage_change) > thresh
            price_sig = abs(price_change) > thresh
            if usage_sig and price_sig:
                return "Usage + Price driven"
            if usage_sig:
                return "Usage-driven"
            if price_sig:
                return "Price-driven"
            return "Stable"

        results = []
        for service, grp in df.groupby("service_name"):
            early = grp[grp["usage_start_date"] <= median_date]
            late = grp[grp["usage_start_date"] > median_date]
            if early.empty or late.empty:
                continue
            early_usage = early["usage_quantity"].mean()
            late_usage = late["usage_quantity"].mean()
            early_price = early["cost_per_quantity_usd"].mean()
            late_price = late["cost_per_quantity_usd"].mean()
            results.append({
                "service_name": service,
                "early_usage": early_usage,
                "late_usage": late_usage,
                "early_price": early_price,
                "late_price": late_price,
                "classification": classify({
                    "early_usage": early_usage,
                    "late_usage": late_usage,
                    "early_price": early_price,
                    "late_price": late_price,
                })
            })
        return pd.DataFrame(results)
    except Exception as e:
        logger.error("Error in usage_vs_price_decomposition: %s", e)
        raise


def target_cost_correlation() -> pd.DataFrame:
    """Average cost per ``target`` action from the ``cloud_usage`` table.

    Returns a DataFrame with ``target`` and ``avg_cost`` columns.
    """
    try:
        query = """
            SELECT target, AVG(cost) AS avg_cost
            FROM cloud_usage
            GROUP BY target;
        """
        with get_connection() as conn:
            df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        logger.error("Error in target_cost_correlation: %s", e)
        raise


def flag_anomalies(z_threshold: float = 2.0, window: int = 12) -> pd.DataFrame:
    """Flag cost anomalies in ``cloud_usage`` using rolling z-score.

    Adds a boolean column ``anomaly_flag``.  The function also returns the same
    DataFrame with the flag column for downstream KPI calculation.
    """
    try:
        with get_connection() as conn:
            df = pd.read_sql_query("SELECT * FROM cloud_usage ORDER BY timestamp", conn)
        df["cost"] = pd.to_numeric(df["cost"], errors="coerce")
        roll_mean = df["cost"].rolling(window=window, center=True).mean()
        roll_std = df["cost"].rolling(window=window, center=True).std()
        z_score = (df["cost"] - roll_mean) / roll_std
        df["anomaly_flag"] = z_score.abs() > z_threshold
        return df
    except Exception as e:
        logger.error("Error in flag_anomalies: %s", e)
        raise


def project_trend(days_forward: int = 7) -> Tuple[pd.DataFrame, float]:
    """Project total daily GCP cost forward using a simple linear fit.

    Returns a tuple ``(proj_df, r_squared)`` where ``proj_df`` contains the
    projected dates and ``projected_cost_usd`` column.
    """
    try:
        query = """
            SELECT DATE(usage_start_date) AS date,
                   SUM(unrounded_cost_usd) AS daily_cost_usd
            FROM gcp_billing
            GROUP BY DATE(usage_start_date)
            ORDER BY date;
        """
        with get_connection() as conn:
            df = pd.read_sql_query(query, conn)
        df["date"] = pd.to_datetime(df["date"])
        x = np.arange(len(df))
        y = df["daily_cost_usd"].values
        coeffs = np.polyfit(x, y, 1)
        fit_line = np.polyval(coeffs, x)
        ss_res = np.sum((y - fit_line) ** 2)
        ss_tot = np.sum((y - y.mean()) ** 2)
        r_squared = 1 - ss_res / ss_tot if ss_tot != 0 else float('nan')
        future_x = np.arange(len(df), len(df) + days_forward)
        future_cost = np.polyval(coeffs, future_x)
        future_dates = pd.date_range(start=df["date"].iloc[-1] + pd.Timedelta(days=1), periods=days_forward)
        proj_df = pd.DataFrame({"date": future_dates, "projected_cost_usd": future_cost})
        return proj_df, r_squared
    except Exception as e:
        logger.error("Error in project_trend: %s", e)
        raise


def optimisation_candidates(utilisation_threshold: float = 50.0) -> pd.DataFrame:
    """Identify GCP services with average CPU utilisation below a threshold.

    Returns ``service_name``, ``avg_cpu_util_pct``, ``total_cost_usd`` and a
    synthetic ``is_synthetic`` flag for transparency.
    """
    try:
        query = """
            SELECT b.service_name,
                   AVG(b.cpu_utilization_pct) AS avg_cpu_util_pct,
                   SUM(b.unrounded_cost_usd) AS total_cost_usd,
                   MAX(t.is_synthetic) AS is_synthetic
            FROM gcp_billing b
            JOIN team_ownership_gcp t ON b.service_name = t.service_name
            GROUP BY b.service_name
            HAVING avg_cpu_util_pct < ?
            ORDER BY total_cost_usd DESC;
        """
        with get_connection() as conn:
            df = pd.read_sql_query(query, conn, params=(utilisation_threshold,))
        return df
    except Exception as e:
        logger.error("Error in optimisation_candidates: %s", e)
        raise


if __name__ == "__main__":
    print("=== Daily Cost Trend ===")
    print(daily_cost_trend().head())
    print("\n=== Cost by GCP Service ===")
    print(cost_by_gcp_service().head())
    print("\n=== Cost by Team ===")
    print(cost_by_team().head())
    print("\n=== Usage vs Price Decomposition ===")
    print(usage_vs_price_decomposition().head())
    print("\n=== Target Cost Correlation ===")
    print(target_cost_correlation())
    print("\n=== Anomaly Flags (first 5 rows) ===")
    print(flag_anomalies().head())
    proj, r2 = project_trend()
    print("\n=== Projection (next 7 days) ===")
    print(proj)
    print(f"R² of linear fit: {r2:.4f}")
    print("\n=== Optimisation Candidates ===")
    print(optimisation_candidates().head())
