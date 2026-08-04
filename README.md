# ☁️ Cloud Infrastructure Cost Attribution

## 📌 Problem Statement

Cloud platforms generate infrastructure billing, deployment history, and service usage metrics as separate datasets. Because these data sources are independent, finance teams often struggle to determine which engineering activities or deployments caused unexpected increases in cloud costs.

This project aims to bridge that gap by correlating billing records, deployment events, and resource usage metrics to identify the root causes of infrastructure cost spikes.

---

## 🎯 Objective

Develop a data analytics dashboard that:

- Detects unusual cloud infrastructure cost spikes.
- Correlates billing data with deployment history.
- Analyzes service usage metrics (CPU, memory, requests, etc.).
- Identifies engineering activities that may have caused increased infrastructure costs.
- Provides actionable insights through an interactive dashboard.

---

## 🚀 Features

- 📊 Cloud billing analysis
- 📈 Cost spike detection
- 🔄 Deployment history tracking
- 📉 Resource usage monitoring
- 🔍 Cost attribution analysis
- 📋 Interactive Streamlit dashboard
- 💾 SQLite database integration
- 📑 Data preprocessing using Pandas & NumPy

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Backend & Data Processing |
| Pandas | Data Cleaning & Analysis |
| NumPy | Numerical Computations |
| Streamlit | Interactive Dashboard |
| SQLite | Database Storage |

---

## 📂 Project Structure

```
Cloud-Infrastructure-Cost-Attribution/
│
├── data/
│   ├── billing.csv
│   ├── deployment_history.csv
│   └── usage_metrics.csv
│
├── database/
│   └── cloud_cost.db
│
├── app.py
├── analysis.py
├── database.py
├── requirements.txt
└── README.md
```

---

## 📊 Dataset

The project uses three datasets:

### 1. Infrastructure Billing
Contains cloud service costs over time.

Example fields:
- Date
- Service
- Region
- Cost

### 2. Deployment History
Records engineering deployments and releases.

Example fields:
- Deployment ID
- Service
- Version
- Engineer
- Timestamp

### 3. Service Usage Metrics
Contains infrastructure utilization data.

Example fields:
- Timestamp
- CPU Usage
- Memory Usage
- Request Count
- Service

---

## ⚙️ Workflow

1. Load cloud billing data.
2. Load deployment history.
3. Load service usage metrics.
4. Clean and preprocess datasets.
5. Store processed data in SQLite.
6. Detect cost anomalies.
7. Correlate cost spikes with deployments and usage metrics.
8. Display insights through a Streamlit dashboard.

---

## 📈 Expected Outcome

The dashboard helps finance and engineering teams:

- Understand why cloud costs increased.
- Identify deployments linked to higher infrastructure spending.
- Monitor resource utilization trends.
- Make informed cost optimization decisions.

---

## 🔮 Future Enhancements

- AI-powered root cause analysis
- Cost forecasting
- Multi-cloud support (AWS, Azure, GCP)
- Automated anomaly detection
- Real-time monitoring integration

---

## 👥 Team

**Alliance University**  
**Semester 5 - Sprint 1**  
**Squad 69 - Team 02**