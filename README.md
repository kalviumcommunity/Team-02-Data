# ☁️ CostLens AI

> **Alliance University · Semester 5 Software Product Engineering · Team 02 · Sprint 1**

A multi-dimensional **cloud cost intelligence dashboard** that correlates infrastructure billing, resource telemetry, and service usage metrics to expose the *root cause* of unexpected cloud spend changes — empowering finance and engineering teams to act, not just observe.

---

## 🔍 Problem Statement

Cloud platforms export infrastructure billing, deployment history, and service usage metrics as **independent, siloed datasets**. Finance teams see cost spikes but cannot attribute them to specific engineering activities or releases. CostLens AI bridges this gap.

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| **Python 3.10+** | Backend data processing |
| **Pandas & NumPy** | Statistical analysis (rolling z-scores, polynomial regression) |
| **SQLite (sqlite3)** | Local 4-table relational database |
| **Streamlit** | Interactive multi-page dashboard |

> ⚠️ **No machine-learning libraries** are used. All anomaly detection and trend projections are powered by pure statistical methods — this is a deliberate Sprint 1 scope decision. Phase 2 will introduce ML forecasting.

---

## 📂 Database Architecture (`costlens.db`)

The local SQLite database contains **4 tables**:

| Table | Source | Description |
|---|---|---|
| `cloud_usage` | Real dataset | Multi-cloud telemetry: CPU, memory, net IO, cost, latency, scaling target (AWS/Azure/GCP, ~1,000 rows, 5-min intervals) |
| `gcp_billing` | Real dataset | GCP billing exports: service, usage quantity, CPU/memory utilisation %, costs in USD & INR (~1,000 rows) |
| `team_ownership_gcp` | **Synthetic** ⚠️ | Maps GCP services → engineering team names. `is_synthetic = True` |
| `team_ownership_cloud` | **Synthetic** ⚠️ | Maps cloud provider + region combos → engineering teams. `is_synthetic = True` |

> **Why separate tables?** The two real datasets share no reliable join key — they cover different cloud scopes and non-overlapping time windows — so they remain independent and are never force-merged.

---

## ⚠️ Data Disclosure

- **Real data**: `cloud_usage` and `gcp_billing` tables use real, publicly available cloud datasets.
- **Synthetic data**: `team_ownership_gcp` and `team_ownership_cloud` contain randomly generated team-to-service assignments. No real organizational ownership data exists publicly. Every dashboard view that shows team-attributed cost includes an explicit synthetic disclaimer.

---

## 🚀 Local Setup & Run

### Step 1 — Clone the repository
```bash
git clone https://github.com/kalviumcommunity/Team-02-Data.git
cd Team-02-Data
```

### Step 2 — Create and activate a virtual environment
```bash
python -m venv venv

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# macOS / Linux
source venv/bin/activate
```

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Initialise the database
```bash
python database.py
```
This ingests the two CSV files from `Data/processed/` and generates the synthetic team-ownership tables.

### Step 5 — Launch the dashboard
```bash
streamlit run Home.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## ☁️ Deployment Guide (Streamlit Community Cloud — Free)

### Prerequisites
- A GitHub account with this repo pushed (public or private).
- A [Streamlit Community Cloud](https://share.streamlit.io) account (free, sign in with GitHub).

### Steps

1. **Commit `costlens.db` to the repo** (or add a `@st.cache_data` startup call that runs `database.py` automatically on first boot — already implemented in the app).

2. **Go to** [share.streamlit.io](https://share.streamlit.io) → **New app**.

3. Fill in:
   | Field | Value |
   |---|---|
   | Repository | `kalviumcommunity/Team-02-Data` |
   | Branch | `main` |
   | Main file path | `Home.py` |

4. Click **Deploy**. Streamlit Cloud reads `requirements.txt` automatically and installs dependencies.

5. The app will be live at a URL like:
   `https://team-02-data.streamlit.app`

### Notes for Cloud Deployment
- `costlens.db` is included in the repo (SQLite files are small and committing them is acceptable for a course project).
- If you prefer not to commit the DB, add this block at the top of `Home.py`:
  ```python
  if not os.path.exists("costlens.db"):
      import database; database.main()
  ```
  This is already in `smoke_test.py` and can be copied over.

---

## 📐 Architecture Overview

```
Home.py                  ← Entry point (global filters, KPI summary, nav guide)
├── components.py        ← Shared reusable UI widgets (kpi_card, charts, badge)
├── filters.py           ← Sidebar input helpers (date, provider, service)
├── analytics.py         ← Pure SQL + Pandas analytics engine (8 functions)
├── database.py          ← SQLite ingestion + synthetic team mapping generator
└── pages/
    ├── 1_Executive_View.py   ← Trend, anomaly count, 7-day projection
    ├── 2_Engineering_View.py ← CPU KPIs, spend breakdown, decomposition table
    └── 3_FinOps_View.py      ← Rightsizing, team attribution, optimisation
```

---

## 📸 Screenshots

*(Add after final run — place screenshots in `screenshots/` folder)*

| View | Preview |
|---|---|
| Home | ![Home](screenshots/home.png) |
| Executive View | ![Executive](screenshots/executive.png) |
| Engineering View | ![Engineering](screenshots/engineering.png) |
| FinOps View | ![FinOps](screenshots/finops.png) |

---

## 👥 Team

| Member | Owned Files |
|---|---|
| **Raghav** | `Home.py`, `components.py`, `filters.py`, `pages/2_Engineering_View.py`, `requirements.txt`, `README.md` |
| **Nahda** | `database.py`, `analytics.py`, `pages/1_Executive_View.py`, `pages/3_FinOps_View.py` |