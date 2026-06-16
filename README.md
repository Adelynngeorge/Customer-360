# Customer Intelligence & Growth Analytics Platform

> End-to-end customer analytics solution featuring RFM segmentation, churn prediction, and A/B testing — built with Python, SQL, and Streamlit.

---

## Overview

This project delivers a full-stack customer analytics platform designed to help businesses understand, retain, and grow their customer base. Using transactional data, it segments customers by **Recency, Frequency, and Monetary Value (RFM)**, predicts **churn risk** via logistic regression, and surfaces insights through an interactive **Streamlit dashboard**.

SQL-driven transformations, Python-based modeling, and Plotly visualizations work together to produce actionable intelligence across the entire customer lifecycle.

---

## Features

- **RFM Segmentation** — Classifies customers into behavioral tiers (Champions, At-Risk, Lost, etc.) using SQL-based scoring logic
- **Churn Prediction Model** — Logistic regression model trained on customer activity features to flag high-risk accounts
- **A/B Testing Framework** — Statistical hypothesis testing to evaluate the impact of campaigns and product changes
- **Interactive Dashboard** — Streamlit + Plotly UI for exploring segments, monitoring KPIs, and filtering by cohort
- **Modular SQL Layer** — All data transformations live in standalone `.sql` files, fully decoupled from Python logic

---

## Tech Stack

| Layer | Tools |
|---|---|
| Database | SQLite |
| Data Processing | Python (pandas, NumPy) |
| Modeling | scikit-learn (logistic regression) |
| Visualization | Plotly |
| Dashboard | Streamlit |
| Query Layer | SQL (standalone `.sql` files) |

---

## Project Structure

```
customer-intelligence-platform/
├── data/
│   ├── raw/                  # Source transaction data
│   └── processed/            # Cleaned and transformed outputs
├── sql/
│   ├── rfm_scoring.sql       # RFM calculation logic
│   ├── churn_features.sql    # Feature engineering queries
│   └── segment_summary.sql   # Aggregation for dashboard
├── notebooks/
│   ├── eda.ipynb             # Exploratory data analysis
│   └── churn_model.ipynb     # Model training and evaluation
├── models/
│   └── churn_model.pkl       # Serialized logistic regression model
├── app/
│   └── dashboard.py          # Streamlit application
├── requirements.txt
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/customer-intelligence-platform.git
cd customer-intelligence-platform

# Install dependencies
pip install -r requirements.txt
```

### Run the Dashboard

```bash
streamlit run app/dashboard.py
```

---

## Key Analyses

### RFM Segmentation
Customers are scored across three dimensions using SQL queries against transactional history. Scores are bucketed into quintiles and mapped to named segments for business interpretation.

| Segment | Description |
|---|---|
| Champions | Bought recently, buy often, spend the most |
| Loyal Customers | Buy regularly, responsive to promotions |
| At Risk | Previously frequent buyers showing reduced activity |
| Lost | Haven't purchased in a long time |

### Churn Prediction
A logistic regression model predicts the probability of churn for each customer based on engineered features including purchase recency, session frequency, average order value, and support ticket history. Model evaluation includes ROC-AUC, precision-recall, and confusion matrix analysis.

### A/B Testing
Hypothesis testing (two-proportion z-test) is used to evaluate the statistical significance of conversion differences between control and treatment groups across marketing campaigns.

## Skills Demonstrated

- Writing production-ready SQL for analytical use cases
- Feature engineering and binary classification with scikit-learn
- Statistical testing and interpreting p-values for business decisions
- Building interactive, filterable dashboards with Streamlit and Plotly
- Structuring a data analytics project for reproducibility and collaboration

---

## Status

