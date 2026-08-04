import pandas as pd

billing = pd.read_csv("data/raw/gcp_final_approved_dataset.csv")
usage = pd.read_csv("data/raw/Cloud_Dataset.csv")

print(billing.head())
print()

print(usage.head())

print()

print(billing.info())

print()

print(usage.info())