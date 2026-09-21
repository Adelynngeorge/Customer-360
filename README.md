# Customer Intelligence & Growth Analytics Platform

> An end-to-end customer analytics platform built with **Python, SQL, machine learning, and Streamlit** to segment customers, identify churn risk, evaluate marketing experiments, and support customer retention and growth decisions.

---

## 📌 Project Overview

The **Customer Intelligence & Growth Analytics Platform** transforms customer transaction and behavioral data into actionable business insights.

The platform focuses on three important customer analytics questions:

1. **Who are our most valuable customers?**
2. **Which customers are at risk of churning?**
3. **Which marketing strategies are actually driving better results?**

The solution combines **SQL-based data transformation, RFM customer segmentation, machine learning, statistical A/B testing, and interactive visualization** to provide a complete view of customer behavior.

An interactive **Streamlit dashboard** allows users to explore customer segments, monitor key performance indicators, identify high-risk customers, and analyze growth opportunities.

---

## 🎯 Business Objectives

The platform is designed to help businesses:

* Identify high-value and loyal customers
* Detect customers showing signs of churn
* Understand purchasing behavior across customer segments
* Support targeted retention and marketing strategies
* Measure the effectiveness of campaigns through A/B testing
* Turn customer data into actionable growth opportunities

---

## 🚀 Key Features

### Customer Segmentation

Uses **Recency, Frequency, and Monetary Value (RFM)** analysis to group customers according to purchasing behavior.

Customers are classified into business-friendly segments such as:

* Champions
* Loyal Customers
* At Risk
* Lost Customers

This segmentation helps businesses prioritize retention campaigns, loyalty programs, and targeted promotions.

### Churn Prediction

A **logistic regression classification model** estimates the probability that a customer will churn.

Customer activity and behavioral features are used to identify accounts that may require proactive retention efforts.

Model performance is evaluated using:

* ROC-AUC
* Precision
* Recall
* Confusion Matrix

### A/B Testing

A statistical experimentation framework evaluates whether differences between **control and treatment groups** are statistically significant.

Two-proportion z-tests are used to analyze conversion performance and determine whether marketing or product changes produced measurable differences.

### Interactive Analytics Dashboard

A **Streamlit and Plotly dashboard** provides an interactive interface for exploring customer intelligence.

Users can:

* Monitor customer KPIs
* Compare customer segments
* Analyze purchasing behavior
* Identify churn-risk customers
* Filter results by customer cohort
* Explore retention and growth opportunities

### Modular SQL Analytics Layer

Core transformations and analytical queries are stored in independent `.sql` files rather than embedded directly within Python.

This structure improves:

* Reusability
* Maintainability
* Reproducibility
* Collaboration

---

## 🛠️ Tech Stack

| Area                 | Technology            |
| -------------------- | --------------------- |
| Database             | SQLite                |
| Data Analysis        | Python, pandas, NumPy |
| Data Transformation  | SQL                   |
| Machine Learning     | scikit-learn          |
| Statistical Analysis | Python                |
| Visualization        | Plotly                |
| Dashboard            | Streamlit             |
| Development          | Jupyter Notebook      |

---

## 📂 Project Structure

```text
customer-intelligence-platform/
│
├── data/
│   ├── raw/                       # Original customer and transaction data
│   └── processed/                 # Cleaned and transformed datasets
│
├── sql/
│   ├── rfm_scoring.sql            # RFM scoring and segmentation
│   ├── churn_features.sql         # Churn feature engineering
│   └── segment_summary.sql        # Customer segment aggregations
│
├── notebooks/
│   ├── eda.ipynb                  # Exploratory data analysis
│   └── churn_model.ipynb          # Churn model development
│
├── models/
│   └── churn_model.pkl            # Trained churn prediction model
│
├── app/
│   └── dashboard.py               # Streamlit dashboard
│
├── requirements.txt
└── README.md
```

---

## 📊 Key Analyses

### 1. RFM Customer Segmentation

Customer transaction history is analyzed across three dimensions:

**Recency** — How recently did the customer make a purchase?

**Frequency** — How often does the customer purchase?

**Monetary Value** — How much does the customer spend?

Customers receive RFM scores and are grouped into behavioral segments.

| Customer Segment | Business Interpretation                                |
| ---------------- | ------------------------------------------------------ |
| Champions        | Recent, frequent, and high-value customers             |
| Loyal Customers  | Consistent customers with strong engagement            |
| At Risk          | Previously active customers showing declining activity |
| Lost Customers   | Customers with extended periods of inactivity          |

These segments can support targeted marketing, loyalty programs, and customer retention strategies.

---

### 2. Churn Risk Analysis

The churn prediction model uses customer behavior and activity features such as:

* Purchase recency
* Purchase frequency
* Average order value
* Customer activity
* Support interaction history

A. logistic regression model** calculates churn probability for individual customers.

High-risk customers can then be identified for potential retention campaigns.



3. Marketing A/B Testing

The platform includes an experimentation framework for comparing marketing or product strategies.

A **two-proportion z-test** evaluates whether conversion-rate differences between control and treatment groups are statistically significant.

This allows businesses to make campaign decisions based on measured results rather than assumptions.

---

## 💡 Business Applications

The insights generated by the platform can support several business functions, including:

Marketing — Identify customer groups for personalized campaigns.

**Customer Retention** — Detect high-risk customers before they disengage.

**Growth Strategy** — Discover high-value customer groups and growth opportunities.

**Product Analytics** — Evaluate how customer behavior changes across products or experiences.

**Expe**
