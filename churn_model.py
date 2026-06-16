import sqlite3
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from datetime import datetime

# Connect to the data warehouse
conn = sqlite3.connect("customer_360.db")

# Pull RFM data plus customer attributes for model features
query = """
    SELECT
        r.customer_id,
        r.customer_name,
        r.customer_segment,
        r.age,
        r.gender,
        r.region_name,
        r.recency,
        r.frequency,
        r.monetary,
        r.r_score,
        r.f_score,
        r.m_score,
        r.rfm_score,
        r.rfm_segment
    FROM RFM_Segments r
"""

df = pd.read_sql_query(query, conn)
conn.close()

# ── Define churn label ─────────────────────────────────────────────────
# A customer is considered churned if they haven't purchased in 90+ days
# This is a common business definition for subscription and retail models
df["churned"] = (df["recency"] >= 90).astype(int)

print(f"Total customers: {len(df)}")
print(f"Churned: {df['churned'].sum()} ({df['churned'].mean()*100:.1f}%)")
print(f"Active:  {(df['churned']==0).sum()} ({(df['churned']==0).mean()*100:.1f}%)")

# ── Feature engineering ────────────────────────────────────────────────
# Convert categorical columns to numbers so sklearn can read them
df["gender_code"] = df["gender"].map({
    "Female": 0, "Male": 1, "Non-Binary": 2
})

df["segment_code"] = df["customer_segment"].map({
    "Budget": 0, "Regular": 1, "Premium": 2
})

df["region_code"] = df["region_name"].map({
    "Northeast": 0, "Southeast": 1, "Midwest": 2,
    "West Coast": 3, "Southwest": 4, "Mid-Atlantic": 5
})

# Features the model will use to predict churn
features = [
    "recency",
    "frequency",
    "monetary",
    "r_score",
    "f_score",
    "m_score",
    "rfm_score",
    "age",
    "gender_code",
    "segment_code",
    "region_code"
]

X = df[features]
y = df["churned"]

# ── Train the churn prediction model ──────────────────────────────────
# Split data — 80% training, 20% testing
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Random Forest works well for customer data — handles mixed feature types
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    max_depth=10
)
model.fit(X_train, y_train)

# ── Evaluate model performance ─────────────────────────────────────────
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\n=== CHURN MODEL RESULTS ===\n")
print(f"Model Accuracy: {accuracy*100:.1f}%")
print(f"\nClassification Report:")
print(classification_report(y_test, y_pred,
      target_names=["Active", "Churned"]))

# ── Feature importance — shows which factors drive churn most ──────────
importance = pd.DataFrame({
    "feature":   features,
    "importance": model.feature_importances_
}).sort_values("importance", ascending=False)

print("Top factors driving churn:")
print("-" * 40)
for _, row in importance.iterrows():
    bar = "█" * int(row["importance"] * 100)
    print(f"  {row['feature']:<15} {row['importance']:.3f}  {bar}")

# ── Score all customers with churn probability ─────────────────────────
df["churn_probability"] = model.predict_proba(X)[:, 1]
df["churn_probability"] = df["churn_probability"].round(3)

# Classify churn risk into three tiers for business action
def churn_risk_tier(prob):
    if prob >= 0.70:
        return "High Risk"
    elif prob >= 0.40:
        return "Medium Risk"
    else:
        return "Low Risk"

df["churn_risk"] = df["churn_probability"].apply(churn_risk_tier)

# ── Save churn predictions back to the database ────────────────────────
conn = sqlite3.connect("customer_360.db")

churn_output = df[[
    "customer_id", "customer_name", "customer_segment",
    "age", "gender", "region_name",
    "recency", "frequency", "monetary",
    "rfm_segment", "churned",
    "churn_probability", "churn_risk"
]]

churn_output.to_sql("Churn_Predictions", conn,
                    if_exists="replace", index=False)
conn.commit()
conn.close()

# ── Print business action summary ─────────────────────────────────────
print(f"\n=== CHURN RISK SUMMARY ===\n")
risk_summary = df.groupby("churn_risk").agg(
    customers        = ("customer_id",       "count"),
    avg_spend        = ("monetary",          "mean"),
    avg_churn_prob   = ("churn_probability", "mean")
).reset_index()

for _, row in risk_summary.iterrows():
    print(f"{row['churn_risk']:<15} "
          f"{int(row['customers']):>4} customers  "
          f"Avg Spend: ${row['avg_spend']:>7,.0f}  "
          f"Avg Churn Prob: {row['avg_churn_prob']:.1%}")

print(f"\n=== HIGH RISK CUSTOMERS TO TARGET ===\n")
high_risk = df[df["churn_risk"] == "High Risk"].nlargest(10, "monetary")
for _, row in high_risk.iterrows():
    print(f"  {row['customer_name']:<25} "
          f"${row['monetary']:>7,.0f} spent  "
          f"Churn Prob: {row['churn_probability']:.1%}  "
          f"Segment: {row['rfm_segment']}")

print("\nChurn predictions saved to customer_360.db")