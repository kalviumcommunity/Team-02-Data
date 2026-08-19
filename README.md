# ☁️ CostLens AI

## 📌 Project Overview
**CostLens AI** is a multi-dimensional cloud cost intelligence dashboard built as a course project for the **Semester 5 Software Product Engineering** course (**Team 02, Alliance University**). 

The platform addresses a major challenge faced by modern engineering and finance teams: **cost attribution**. While cloud platforms export raw infrastructure billing, deployment history, and service usage metrics as independent datasets, finance teams often struggle to attribute sudden cost spikes to specific engineering activities or code releases. CostLens AI correlates these datasets to identify the root causes of infrastructure spend changes.

---

## 🛠️ Tech Stack
This project is built strictly using the following approved stack:
* **Python** (Backend Logic & Data Ingestion)
* **Pandas & NumPy** (Data Cleaning & Statistical Analysis)
* **SQLite (SQL)** (Local Data Storage & Querying)
* **Streamlit** (Interactive Dashboard Web Interface)

*No machine learning libraries (such as scikit-learn or TensorFlow) are used in this codebase to adhere to the Sprint 1 statistical scope.*

---

## 📂 Database Architecture
Data is ingested and stored locally in a SQLite database (`costlens.db`) consisting of **4 tables**:

1. **`cloud_usage`**: Contains multi-cloud telemetry data (AWS, Azure, GCP) covering virtual machine specs, utilization percentages, IO rates, costs, response times, and automated scaling recommendations (`target`).
2. **`gcp_billing`**: Houses raw Google Cloud Platform billing metrics, usage quantities, billing duration, and costs in USD and INR.
3. **`team_ownership_gcp`** *(Synthetic)*: Maps GCP services to responsible engineering teams. Contains an `is_synthetic=True` transparency flag.
4. **`team_ownership_cloud`** *(Synthetic)*: Maps multi-cloud provider and region combinations to responsible engineering teams. Contains an `is_synthetic=True` transparency flag.

---

## 💡 Important Disclosures

> [!NOTE]
> **Sprint 1 Statistical-Only Scope**  
> All features in this release are powered by pure statistical methods (such as rolling standard deviation Z-Scores for anomaly detection, and linear regression fits for trend projection). No machine learning is active in Sprint 1, in strict alignment with Phase 1 of our Product Requirements Document (PRD). Machine learning forecasting models are scheduled for the Phase 2 upgrade plan.

> [!IMPORTANT]
> **Real vs. Synthetic Data Disclosure**  
> Because real organizational team mapping data is not publicly available, the team allocation datasets (`team_ownership_gcp` and `team_ownership_cloud`) are **100% synthetic**. This synthetic nature is visually indicated wherever team-based costs are rendered.

---

## 🚀 Setup & Installation

Follow these steps to run the application locally on your machine:

### 1. Clone the Repository
```bash
git clone https://github.com/kalviumcommunity/Team-02-Data.git
cd Team-02-Data
```

### 2. Set Up a Virtual Environment & Install Dependencies
Create a virtual environment and install the required, pinned packages:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt
```

### 3. Initialize the SQLite Database
Ingest the preprocessed CSV datasets and generate the synthetic team-ownership mappings:
```bash
python database.py
```

### 4. Run the Streamlit Dashboard
Launch the web interface locally:
```bash
streamlit run Home.py
```

---

## 🖥️ UI Screenshots (Placeholders)

Below are the layout structures for the main views of the application:

### Home Screen
*Visual entry point and multi-cloud summary metrics:*  
![Home Screen Placeholder](screenshots/home.png)

### Executive View
*High-level spending trends, team-wise cost breakdown, and linear projections:*  
![Executive View Placeholder](screenshots/executive.png)

### Engineering View
*Resource utilization profiles, anomaly indicators, and price-vs-usage decomposition tables:*  
![Engineering View Placeholder](screenshots/engineering.png)

### FinOps View
*Rightsizing recommendations, idle resources tracking, and unit cost KPIs:*  
![FinOps View Placeholder](screenshots/finops.png)