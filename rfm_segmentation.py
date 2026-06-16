
import sqlite3
import pandas as pd
from datetime import datetime

conn = sqlite3.connect("customer_360.db")

query = """
    SELECT
        c.customer_id,
        c.first_name || ' ' || c.last_name AS customer_name,
        c.customer_segment,
        c.age,
        c.gender,
        r.region_name,
        o.date_id,
        o.total_amount
    FROM Fact_Orders o
    JOIN Dim_Customers c ON c.customer_id = o.customer_id
    JOIN Dim_Regions r   ON r.region_id   = o.region_id
    WHERE o.status = 'Completed'
"""

df = pd.read_sql_query(query, conn)
conn.close()

print(f"Rows loaded: {len(df)}")

df["order_date"] = pd.to_datetime(df["date_id"] + "-01", errors="coerce")
df["total_amount"] = pd.to_numeric(df["total_amount"], errors="coerce")
df = df.dropna(subset=["order_date", "total_amount"])

print(f"Rows after cleaning: {len(df)}")

snapshot_date = datetime(2026, 6, 15)

rfm = df.groupby(["customer_id","customer_name","customer_segment",
                   "age","gender","region_name"]).agg(
    recency   = ("order_date",   lambda x: (snapshot_date - x.max()).days),
    frequency = ("order_date",   "count"),
    monetary  = ("total_amount", "sum")
).reset_index()

rfm["monetary"]  = rfm["monetary"].astype(float).round(2)
rfm["recency"]   = rfm["recency"].astype(float)
rfm["frequency"] = rfm["frequency"].astype(float)

print(f"Customers in RFM: {len(rfm)}")

# Score using simple ranking divided into 5 equal groups
def make_score(series, ascending=True):
    ranks = series.rank(method="first")
    n = len(ranks)
    scores = ((ranks - 1) / n * 5).astype(int) + 1
    scores = scores.clip(1, 5)
    if not ascending:
        scores = 6 - scores
    return scores

rfm["r_score"] = make_score(rfm["recency"],   ascending=False)
rfm["f_score"] = make_score(rfm["frequency"], ascending=True)
rfm["m_score"] = make_score(rfm["monetary"],  ascending=True)
rfm["rfm_score"] = rfm["r_score"] + rfm["f_score"] + rfm["m_score"]

def classify_customer(row):
    r = row["r_score"]
    f = row["f_score"]
    m = row["m_score"]
    if r >= 4 and f >= 4 and m >= 4:
        return "Champions"
    elif r >= 3 and f >= 3:
        return "Loyal Customers"
    elif r >= 3 and f <= 2:
        return "Potential Loyalists"
    elif r <= 2 and f >= 3:
        return "At Risk"
    else:
        return "Lost Customers"

rfm["rfm_segment"] = rfm.apply(classify_customer, axis=1)

# Save to database
conn = sqlite3.connect("customer_360.db")
cur = conn.cursor()
cur.execute("DROP TABLE IF EXISTS RFM_Segments")
conn.commit()
rfm.to_sql("RFM_Segments", conn, if_exists="replace", index=False)
conn.commit()
conn.close()

# Verify it saved
conn = sqlite3.connect("customer_360.db")
count = pd.read_sql_query("SELECT COUNT(*) as cnt FROM RFM_Segments", conn)
print(f"RFM rows saved: {count['cnt'][0]}")
conn.close()

print("\n=== RFM SEGMENTATION COMPLETE ===\n")
segment_order = ["Champions","Loyal Customers","Potential Loyalists",
                 "At Risk","Lost Customers"]

summary = rfm.groupby("rfm_segment").agg(
    customers  = ("customer_id", "count"),
    avg_spend  = ("monetary",    "mean"),
    avg_orders = ("frequency",   "mean"),
    avg_days   = ("recency",     "mean")
).reindex(segment_order).reset_index()

for _, row in summary.iterrows():
    if pd.isna(row["customers"]):
        continue
    print(f"{row['rfm_segment']:<22} {int(row['customers']):>4} customers  "
          f"Avg Spend: ${row['avg_spend']:>8,.0f}  "
          f"Avg Orders: {row['avg_orders']:>4.1f}")

print("\nRFM results saved to customer_360.db")