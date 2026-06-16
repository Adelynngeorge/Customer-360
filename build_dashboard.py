import sqlite3
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, LineChart, PieChart, Reference
from openpyxl.utils import get_column_letter

conn = sqlite3.connect("customer_360.db")

orders_df = pd.read_sql_query("""
    SELECT o.*, c.customer_segment, r.region_name
    FROM Fact_Orders o
    JOIN Dim_Customers c ON c.customer_id = o.customer_id
    JOIN Dim_Regions r   ON r.region_id   = o.region_id
    WHERE o.status = 'Completed'
""", conn)

products_df = pd.read_sql_query("""
    SELECT oi.*, p.product_name, p.category, p.brand
    FROM Fact_Order_Items oi
    JOIN Dim_Products p ON p.product_id = oi.product_id
    JOIN Fact_Orders o  ON o.order_id   = oi.order_id
    WHERE o.status = 'Completed'
""", conn)

rfm_df     = pd.read_sql_query("SELECT * FROM RFM_Segments",     conn)
churn_df   = pd.read_sql_query("SELECT * FROM Churn_Predictions", conn)

regional_df = pd.read_sql_query("""
    SELECT r.region_name,
           COUNT(DISTINCT c.customer_id) AS customers,
           COUNT(DISTINCT o.order_id)    AS orders,
           ROUND(SUM(o.total_amount), 2) AS revenue
    FROM Dim_Regions r
    JOIN Dim_Customers c ON c.region_id   = r.region_id
    JOIN Fact_Orders o   ON o.customer_id = c.customer_id
    WHERE o.status = 'Completed'
    GROUP BY r.region_name ORDER BY revenue DESC
""", conn)

monthly_df = pd.read_sql_query("""
    SELECT date_id AS month,
           COUNT(DISTINCT order_id)    AS orders,
           ROUND(SUM(total_amount), 2) AS revenue
    FROM Fact_Orders
    WHERE status = 'Completed'
    GROUP BY date_id ORDER BY date_id
""", conn)

conn.close()

# ── Color palette — olive green, blue, white theme ─────────────────────
NAVY   = "1B3A2D"
TEAL   = "2E5E4E"
GREEN  = "556B2F"
OLIVE  = "4A7C59"
GOLD   = "8FBC8F"
RED    = "C0392B"
WHITE  = "FFFFFF"
LGRAY  = "F5F5F0"
BLUE   = "1B3A6B"
FONT   = "Times New Roman"
TODAY  = "June 15, 2026"
AUTHOR = "Adelynn Neha George"
TITLE  = "Beauty & Skincare Customer Intelligence Platform"

def hdr_fill(hex_color):
    return PatternFill("solid", start_color=hex_color, end_color=hex_color)

def hdr_font(bold=True, color=WHITE, size=11):
    return Font(bold=bold, color=color, size=size, name=FONT)

def body_font(size=10, bold=False, color="000000"):
    return Font(size=size, name=FONT, bold=bold, color=color)

def thin_border():
    s = Side(border_style="thin", color="D9DDE0")
    return Border(left=s, right=s, top=s, bottom=s)

def center():
    return Alignment(horizontal="center", vertical="center", wrap_text=True)

def style_header(cell, bg=NAVY):
    cell.fill = hdr_fill(bg)
    cell.font = hdr_font()
    cell.alignment = center()
    cell.border = thin_border()

def add_title(ws, text, row, cols, bg=NAVY):
    ws.merge_cells(start_row=row, start_column=1,
                   end_row=row, end_column=cols)
    cell = ws.cell(row=row, column=1, value=text)
    cell.fill = hdr_fill(bg)
    cell.font = hdr_font(size=14)
    cell.alignment = center()
    ws.row_dimensions[row].height = 40

def add_section(ws, text, row, cols, bg=TEAL):
    ws.merge_cells(start_row=row, start_column=1,
                   end_row=row, end_column=cols)
    cell = ws.cell(row=row, column=1, value=text)
    cell.fill = hdr_fill(bg)
    cell.font = hdr_font(size=11)
    cell.alignment = center()
    ws.row_dimensions[row].height = 22

def add_data_row(ws, row, values, alt=False):
    bg = LGRAY if alt else WHITE
    for j, val in enumerate(values, 1):
        cell = ws.cell(row=row, column=j, value=val)
        cell.fill = hdr_fill(bg)
        cell.font = body_font()
        cell.border = thin_border()
        cell.alignment = center()
    ws.row_dimensions[row].height = 18

def add_kpi(ws, label, value, row, col, color=NAVY, span=2):
    ws.merge_cells(start_row=row, start_column=col,
                   end_row=row, end_column=col+span-1)
    lc = ws.cell(row=row, column=col, value=label)
    lc.fill = hdr_fill(color)
    lc.font = hdr_font(bold=False, size=10)
    lc.alignment = center()
    ws.row_dimensions[row].height = 22
    ws.merge_cells(start_row=row+1, start_column=col,
                   end_row=row+1, end_column=col+span-1)
    vc = ws.cell(row=row+1, column=col, value=value)
    vc.fill = hdr_fill(color)
    vc.font = Font(bold=True, size=18, color=WHITE, name=FONT)
    vc.alignment = center()
    ws.row_dimensions[row+1].height = 40

wb = Workbook()

# ══════════════════════════════════════════════════════════════════════
# SHEET 1: EXECUTIVE SUMMARY
# ══════════════════════════════════════════════════════════════════════
ws1 = wb.active
ws1.title = "Executive Summary"
ws1.sheet_view.showGridLines = False

# Title with project name
add_title(ws1, TITLE, 1, 10, bg=NAVY)

# Author on left, date on right
ws1.merge_cells("A2:G2")
sub = ws1["A2"]
sub.value = f"By {AUTHOR}  |  Liberty University  |  Portfolio Project"
sub.fill = hdr_fill(GREEN)
sub.font = hdr_font(bold=False, size=11)
sub.alignment = center()
ws1.row_dimensions[2].height = 22

ws1.cell(row=2, column=8).value = TODAY
ws1.cell(row=2, column=8).fill = hdr_fill(BLUE)
ws1.cell(row=2, column=8).font = hdr_font(bold=False, size=11)
ws1.cell(row=2, column=8).alignment = center()

# KPI cards
total_rev     = orders_df["total_amount"].sum()
total_orders  = len(orders_df)
total_custs   = orders_df["customer_id"].nunique()
avg_order_val = orders_df["total_amount"].mean()
high_risk     = len(churn_df[churn_df["churn_risk"] == "High Risk"])
champions     = len(rfm_df[rfm_df["rfm_segment"] == "Champions"])

ws1.row_dimensions[3].height = 10
add_kpi(ws1, "Total Revenue",   f"${total_rev:,.0f}",    4, 1, NAVY)
add_kpi(ws1, "Total Orders",    f"{total_orders:,}",     4, 3, TEAL)
add_kpi(ws1, "Total Customers", f"{total_custs:,}",      4, 5, GREEN)
add_kpi(ws1, "Avg Order Value", f"${avg_order_val:,.0f}",4, 7, OLIVE)
add_kpi(ws1, "High Risk",       f"{high_risk}",          4, 9, RED)

ws1.row_dimensions[6].height = 10
at_risk   = len(rfm_df[rfm_df["rfm_segment"] == "At Risk"])
lost      = len(rfm_df[rfm_df["rfm_segment"] == "Lost Customers"])
loyal     = len(rfm_df[rfm_df["rfm_segment"] == "Loyal Customers"])
potential = len(rfm_df[rfm_df["rfm_segment"] == "Potential Loyalists"])
add_kpi(ws1, "Champions",       f"{champions}",  7, 1, GREEN)
add_kpi(ws1, "Loyal Customers", f"{loyal}",      7, 3, TEAL)
add_kpi(ws1, "Potential",       f"{potential}",  7, 5, OLIVE)
add_kpi(ws1, "At Risk",         f"{at_risk}",    7, 7, RED)
add_kpi(ws1, "Lost",            f"{lost}",       7, 9, NAVY)

ws1.row_dimensions[9].height = 10

# Segment summary table
add_section(ws1, "CUSTOMER SEGMENT SUMMARY", 10, 5, bg=TEAL)
for j, h in enumerate(["Segment","Customers","Avg Spend","Avg Orders","Avg Days Since Buy"], 1):
    style_header(ws1.cell(row=11, column=j, value=h), bg=NAVY)
ws1.row_dimensions[11].height = 22

segment_order = ["Champions","Loyal Customers","Potential Loyalists",
                 "At Risk","Lost Customers"]
seg_summary = rfm_df.groupby("rfm_segment").agg(
    customers  = ("customer_id", "count"),
    avg_spend  = ("monetary",    "mean"),
    avg_orders = ("frequency",   "mean"),
    avg_days   = ("recency",     "mean")
).reindex(segment_order).reset_index()

for i, row in seg_summary.iterrows():
    if pd.isna(row["customers"]):
        continue
    vals = [row["rfm_segment"], int(row["customers"]),
            f"${row['avg_spend']:,.0f}", f"{row['avg_orders']:.1f}",
            f"{row['avg_days']:.0f} days"]
    add_data_row(ws1, 12+i, vals, alt=i%2==1)

ws1.row_dimensions[17].height = 10

# Top 5 products
add_section(ws1, "TOP 5 PRODUCTS BY REVENUE", 18, 5, bg=TEAL)
for j, h in enumerate(["Product","Category","Units Sold","Revenue","Brand"], 1):
    style_header(ws1.cell(row=19, column=j, value=h), bg=NAVY)
ws1.row_dimensions[19].height = 22

top_products = products_df.groupby(["product_name","category","brand"]).agg(
    units   = ("quantity",    "sum"),
    revenue = ("total_price", "sum")
).reset_index().nlargest(5, "revenue")

for i, row in top_products.iterrows():
    vals = [row["product_name"], row["category"],
            int(row["units"]), f"${row['revenue']:,.0f}", row["brand"]]
    add_data_row(ws1, 20+i, vals, alt=i%2==1)

for col, width in zip("ABCDEFGHIJ", [22,12,14,14,14,10,10,14,10,10]):
    ws1.column_dimensions[col].width = width

# ══════════════════════════════════════════════════════════════════════
# SHEET 2: CUSTOMER HEALTH
# ══════════════════════════════════════════════════════════════════════
ws2 = wb.create_sheet("Customer Health")
ws2.sheet_view.showGridLines = False

add_title(ws2, "CUSTOMER HEALTH & CHURN ANALYSIS", 1, 8, bg=NAVY)

add_section(ws2, "CHURN RISK BREAKDOWN", 3, 5, bg=RED)
for j, h in enumerate(["Risk Tier","Customers","Avg Spend","Avg Churn Prob","Action"], 1):
    style_header(ws2.cell(row=4, column=j, value=h), bg=NAVY)
ws2.row_dimensions[4].height = 22

risk_summary = churn_df.groupby("churn_risk").agg(
    customers      = ("customer_id",       "count"),
    avg_spend      = ("monetary",          "mean"),
    avg_churn_prob = ("churn_probability", "mean")
).reset_index()

actions = {
    "High Risk":   "Immediate win-back campaign",
    "Medium Risk": "Loyalty rewards offer",
    "Low Risk":    "Upsell premium products"
}

for i, row in risk_summary.iterrows():
    vals = [row["churn_risk"], int(row["customers"]),
            f"${row['avg_spend']:,.0f}", f"{row['avg_churn_prob']:.1%}",
            actions.get(row["churn_risk"], "")]
    add_data_row(ws2, 5+i, vals, alt=i%2==1)

ws2.row_dimensions[8].height = 10

add_section(ws2, "HIGH RISK CUSTOMERS — IMMEDIATE ACTION REQUIRED", 9, 7, bg=RED)
for j, h in enumerate(["Customer","Segment","Region","Spent","Orders","Churn Prob","RFM Segment"], 1):
    style_header(ws2.cell(row=10, column=j, value=h), bg=NAVY)
ws2.row_dimensions[10].height = 22

high_risk_df = churn_df[churn_df["churn_risk"] == "High Risk"].nlargest(20, "monetary").reset_index(drop=True)
for i, row in high_risk_df.iterrows():
    vals = [row["customer_name"], row["customer_segment"], row["region_name"],
            f"${row['monetary']:,.0f}", int(row["frequency"]),
            f"{row['churn_probability']:.1%}", row["rfm_segment"]]
    add_data_row(ws2, 11+i, vals, alt=i%2==1)

# Pie chart
seg_counts = rfm_df["rfm_segment"].value_counts().reindex(segment_order)
chart_start = 32
for i, (seg, count) in enumerate(seg_counts.items()):
    ws2.cell(row=chart_start+i, column=1, value=seg)
    ws2.cell(row=chart_start+i, column=2, value=int(count))

pc = PieChart()
pc.title = "Customer Segments"
pc.style = 10
pc.width = 18
pc.height = 13
cats = Reference(ws2, min_col=1, min_row=chart_start,
                 max_row=chart_start+len(seg_counts)-1)
vals = Reference(ws2, min_col=2, min_row=chart_start,
                 max_row=chart_start+len(seg_counts)-1)
pc.add_data(vals)
pc.set_categories(cats)
ws2.add_chart(pc, "I3")

for col, width in zip("ABCDEFGH", [24,14,14,14,10,12,18,10]):
    ws2.column_dimensions[col].width = width

# ══════════════════════════════════════════════════════════════════════
# SHEET 3: REVENUE TRENDS
# ══════════════════════════════════════════════════════════════════════
ws3 = wb.create_sheet("Revenue Trends")
ws3.sheet_view.showGridLines = False

add_title(ws3, "REVENUE TRENDS ANALYSIS", 1, 5, bg=NAVY)

add_section(ws3, "MONTHLY REVENUE", 3, 3, bg=TEAL)
for j, h in enumerate(["Month","Orders","Revenue"], 1):
    style_header(ws3.cell(row=4, column=j, value=h), bg=NAVY)
ws3.row_dimensions[4].height = 22

for i, row in monthly_df.iterrows():
    add_data_row(ws3, 5+i, [row["month"], int(row["orders"]), row["revenue"]],
                 alt=i%2==1)

end_row = 5 + len(monthly_df) - 1
lc = LineChart()
lc.title = "Monthly Revenue Trend"
lc.style = 10
lc.width = 28
lc.height = 15
cats = Reference(ws3, min_col=1, min_row=5, max_row=end_row)
vals = Reference(ws3, min_col=3, min_row=4, max_row=end_row)
lc.add_data(vals, titles_from_data=True)
lc.set_categories(cats)
ws3.add_chart(lc, "E3")

seg_rev   = orders_df.groupby("customer_segment")["total_amount"].sum().reset_index()
seg_start = end_row + 3
add_section(ws3, "REVENUE BY CUSTOMER SEGMENT", seg_start, 3, bg=TEAL)
for j, h in enumerate(["Segment","Revenue","% of Total"], 1):
    style_header(ws3.cell(row=seg_start+1, column=j, value=h), bg=NAVY)

total = seg_rev["total_amount"].sum()
for i, row in seg_rev.iterrows():
    vals = [row["customer_segment"], f"${row['total_amount']:,.0f}",
            f"{row['total_amount']/total*100:.1f}%"]
    add_data_row(ws3, seg_start+2+i, vals, alt=i%2==1)

for col, width in zip("ABCDE", [16,12,16,10,10]):
    ws3.column_dimensions[col].width = width

# ══════════════════════════════════════════════════════════════════════
# SHEET 4: PRODUCT ANALYSIS
# ══════════════════════════════════════════════════════════════════════
ws4 = wb.create_sheet("Product Analysis")
ws4.sheet_view.showGridLines = False

add_title(ws4, "PRODUCT PERFORMANCE ANALYSIS", 1, 6, bg=NAVY)

product_rev = products_df.groupby(["product_name","category","brand"]).agg(
    units   = ("quantity",    "sum"),
    revenue = ("total_price", "sum")
).reset_index().sort_values("revenue", ascending=False)

add_section(ws4, "REVENUE BY PRODUCT", 3, 5, bg=TEAL)
for j, h in enumerate(["Product","Category","Brand","Units Sold","Revenue"], 1):
    style_header(ws4.cell(row=4, column=j, value=h), bg=NAVY)
ws4.row_dimensions[4].height = 22

for i, row in product_rev.iterrows():
    vals = [row["product_name"], row["category"], row["brand"],
            int(row["units"]), row["revenue"]]
    add_data_row(ws4, 5+i, vals, alt=i%2==1)

prod_end = 5 + len(product_rev) - 1
chart = BarChart()
chart.type = "bar"
chart.title = "Revenue by Product"
chart.style = 10
chart.width = 22
chart.height = 16
cats = Reference(ws4, min_col=1, min_row=5, max_row=prod_end)
vals = Reference(ws4, min_col=5, min_row=4, max_row=prod_end)
chart.add_data(vals, titles_from_data=True)
chart.set_categories(cats)
ws4.add_chart(chart, "G3")

cat_rev = products_df.groupby("category")["total_price"].sum().reset_index()
cat_rev.columns = ["category","revenue"]
cat_rev = cat_rev.sort_values("revenue", ascending=False)

cat_start = prod_end + 3
add_section(ws4, "REVENUE BY CATEGORY", cat_start, 3, bg=TEAL)
for j, h in enumerate(["Category","Revenue","% of Total"], 1):
    style_header(ws4.cell(row=cat_start+1, column=j, value=h), bg=NAVY)

total_prod = cat_rev["revenue"].sum()
for i, row in cat_rev.iterrows():
    vals = [row["category"], f"${row['revenue']:,.0f}",
            f"{row['revenue']/total_prod*100:.1f}%"]
    add_data_row(ws4, cat_start+2+i, vals, alt=i%2==1)

for col, width in zip("ABCDEFG", [26,14,14,12,14,10,10]):
    ws4.column_dimensions[col].width = width

# ══════════════════════════════════════════════════════════════════════
# SHEET 5: REGIONAL ANALYSIS
# ══════════════════════════════════════════════════════════════════════
ws5 = wb.create_sheet("Regional Analysis")
ws5.sheet_view.showGridLines = False

add_title(ws5, "REGIONAL PERFORMANCE ANALYSIS", 1, 6, bg=NAVY)

add_section(ws5, "REVENUE BY REGION", 3, 5, bg=TEAL)
for j, h in enumerate(["Region","Customers","Orders","Revenue","Rev/Customer"], 1):
    style_header(ws5.cell(row=4, column=j, value=h), bg=NAVY)
ws5.row_dimensions[4].height = 22

for i, row in regional_df.iterrows():
    rev_per_cust = row["revenue"] / row["customers"] if row["customers"] > 0 else 0
    vals = [row["region_name"], int(row["customers"]),
            int(row["orders"]), row["revenue"], round(rev_per_cust, 2)]
    add_data_row(ws5, 5+i, vals, alt=i%2==1)

reg_end = 5 + len(regional_df) - 1
chart2 = BarChart()
chart2.type = "col"
chart2.title = "Revenue by Region"
chart2.style = 10
chart2.width = 20
chart2.height = 13
cats = Reference(ws5, min_col=1, min_row=5, max_row=reg_end)
vals = Reference(ws5, min_col=4, min_row=4, max_row=reg_end)
chart2.add_data(vals, titles_from_data=True)
chart2.set_categories(cats)
ws5.add_chart(chart2, "G3")

reg_churn = churn_df.groupby("region_name").agg(
    customers = ("customer_id",       "count"),
    high_risk = ("churn_risk",        lambda x: (x=="High Risk").sum()),
    avg_prob  = ("churn_probability", "mean")
).reset_index()

reg_start = reg_end + 3
add_section(ws5, "CHURN RISK BY REGION", reg_start, 4, bg=NAVY)
for j, h in enumerate(["Region","Customers","High Risk","Avg Churn Prob"], 1):
    style_header(ws5.cell(row=reg_start+1, column=j, value=h), bg=GREEN)

for i, row in reg_churn.iterrows():
    vals = [row["region_name"], int(row["customers"]),
            int(row["high_risk"]), f"{row['avg_prob']:.1%}"]
    add_data_row(ws5, reg_start+2+i, vals, alt=i%2==1)

for col, width in zip("ABCDEFG", [18,12,12,16,16,10,10]):
    ws5.column_dimensions[col].width = width

# Save
wb.save("outputs/Customer_360_Dashboard.xlsx")
print("\nDashboard saved to outputs/Customer_360_Dashboard.xlsx")
print("\nSheets created:")
print("  1. Executive Summary")
print("  2. Customer Health")
print("  3. Revenue Trends")
print("  4. Product Analysis")
print("  5. Regional Analysis")