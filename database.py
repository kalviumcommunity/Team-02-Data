"""
CostLens AI Database Setup Script

This script loads the preprocessed datasets into a local SQLite database (costlens.db).

Why the datasets are kept separate (NO MERGING):
The two datasets (Cloud_Dataset_cleaned.csv and gcp_dataset_cleaned.csv) do not share
a reliable join key.
1. Cloud_Dataset_cleaned spans multi-cloud telemetry (AWS, Azure, GCP) but only covers
   a ~3.5-day duration at a 5-minute granularity.
2. gcp_dataset_cleaned covers billing data exclusively for Google Cloud Platform (GCP)
   spanning 2+ months at a coarser per-resource billing window resolution.
Because they represent different scopes of metrics, cloud providers, and non-overlapping
temporal scales, they are loaded as separate tables (`cloud_usage` and `gcp_billing`)
rather than being merged into a single table.
"""

import os
import sqlite3
import random
import pandas as pd

def main():
    db_path = "costlens.db"
    cloud_usage_path = "Data/processed/Cloud_Dataset_cleaned.csv"
    gcp_billing_path = "Data/processed/gcp_dataset_cleaned.csv"
    
    conn = None
    try:
        # 1. Establish database connection
        print(f"Connecting to database: {db_path}...")
        conn = sqlite3.connect(db_path)
        
        # 2. Check for existence of the cleaned CSV files
        if not os.path.exists(cloud_usage_path):
            raise FileNotFoundError(f"Cleaned cloud telemetry dataset not found: '{cloud_usage_path}'")
        if not os.path.exists(gcp_billing_path):
            raise FileNotFoundError(f"Cleaned GCP billing dataset not found: '{gcp_billing_path}'")
        
        # 3. Read processed datasets with error handling for malformed CSVs
        try:
            print("Reading Cloud telemetry dataset...")
            df_cloud = pd.read_csv(cloud_usage_path, parse_dates=['timestamp'])
        except pd.errors.ParserError as e:
            raise ValueError(f"Cloud dataset CSV is malformed or corrupted: {e}")
            
        try:
            print("Reading GCP billing dataset...")
            df_gcp = pd.read_csv(gcp_billing_path, parse_dates=['usage_start_date', 'usage_end_date'])
        except pd.errors.ParserError as e:
            raise ValueError(f"GCP billing CSV is malformed or corrupted: {e}")
        
        # 4. Load datasets into SQLite (using if_exists="replace" to allow safe re-running)
        print("Loading cloud_usage table into SQLite...")
        df_cloud.to_sql("cloud_usage", conn, if_exists="replace", index=False)
        
        print("Loading gcp_billing table into SQLite...")
        df_gcp.to_sql("gcp_billing", conn, if_exists="replace", index=False)
        
        # 5. Generate synthetic team-ownership tables
        random.seed(42)
        teams = ["Platform Team", "Data Engineering", "Payments Team", "Core Infra", "ML Team"]
        
        # Generate team_ownership_gcp (unique service names mapped to teams)
        # Sorting service names guarantees deterministic random assignment
        gcp_services = sorted(df_gcp['service_name'].unique())
        ownership_gcp = pd.DataFrame({
            "service_name": gcp_services,
            "team_name": [random.choice(teams) for _ in gcp_services],
            "is_synthetic": True
        })
        
        # Generate team_ownership_cloud (unique cloud provider + region combos mapped to teams)
        # Sorting combinations guarantees deterministic random assignment
        providers_regions = (
            df_cloud[['cloud_provider', 'region']]
            .drop_duplicates()
            .sort_values(by=['cloud_provider', 'region'])
            .reset_index(drop=True)
        )
        providers_regions['team_name'] = [random.choice(teams) for _ in range(len(providers_regions))]
        providers_regions['is_synthetic'] = True
        
        # Write synthetic tables to SQL
        print("Loading team_ownership_gcp table into SQLite...")
        ownership_gcp.to_sql("team_ownership_gcp", conn, if_exists="replace", index=False)
        
        print("Loading team_ownership_cloud table into SQLite...")
        providers_regions.to_sql("team_ownership_cloud", conn, if_exists="replace", index=False)
        
        # Commit transaction
        conn.commit()
        print("Database transaction committed successfully.")
        
        # 6. Print table names and row counts for verification
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [r[0] for r in cur.fetchall()]
        
        print("\n--- Database Verification ---")
        for table in sorted(tables):
            cur.execute(f"SELECT COUNT(*) FROM {table};")
            row_count = cur.fetchone()[0]
            print(f"Table: {table:<25} | Rows: {row_count}")
        print("-----------------------------\n")
        
    except FileNotFoundError as fnf_err:
        print(f"File Error: {fnf_err}")
    except ValueError as val_err:
        print(f"Data Parsing Error: {val_err}")
    except sqlite3.Error as sql_err:
        print(f"SQLite Database Error: {sql_err}")
    except Exception as e:
        print(f"Unexpected Error: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    main()