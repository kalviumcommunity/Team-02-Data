import pandas as pd
import sqlite3
import random
conn = sqlite3.connect("costlens.db")
df1 = pd.read_csv("Data/processed/Cloud_Dataset_cleaned.csv", parse_dates=['timestamp'])
df2 = pd.read_csv("Data/processed/gcp_dataset_cleaned.csv", parse_dates=['usage_start_date', 'usage_end_date'])
df1.to_sql("cloud_usage", conn, if_exists="replace", index=False)
df2.to_sql("gcp_billing", conn, if_exists="replace", index=False)
random.seed(42)   # makes the "random" team assignment repeatable every time you run this
teams = ["Platform Team", "Data Engineering", "Payments Team", "Core Infra", "ML Team"]

gcp_services = df2['service_name'].unique()      # get each distinct GCP service name, once
ownership_gcp = pd.DataFrame({
    "service_name": gcp_services,
    "team_name": [random.choice(teams) for _ in gcp_services],   # assign a random team to each
    "is_synthetic": True     # honesty flag — marks this as simulated, not real data
})

providers_regions = df1[['cloud_provider', 'region']].drop_duplicates()
providers_regions['team_name'] = [random.choice(teams) for _ in range(len(providers_regions))]
providers_regions['is_synthetic'] = True

ownership_gcp.to_sql("team_ownership_gcp", conn, if_exists="replace", index=False)
providers_regions.to_sql("team_ownership_cloud", conn, if_exists="replace", index=False)
conn.commit()   # writes everything to disk permanently

cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Tables created:", [r[0] for r in cur.fetchall()])

conn.close()   # always close the connection when you're done