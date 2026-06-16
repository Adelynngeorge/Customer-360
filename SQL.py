-- ============================================================
-- Customer 360 Analytics Queries
-- Database: customer_360.db (SQLite)
-- ============================================================


-- ─────────────────────────────────────────
-- 1. REVENUE OVERVIEW
-- ─────────────────────────────────────────

-- Total revenue, orders, and AOV by year
SELECT
    d.year,
    COUNT(DISTINCT o.order_id)          AS total_orders,
    ROUND(SUM(o.total_amount), 2)       AS gross_revenue,
    ROUND(AVG(o.total_amount), 2)       AS avg_order_value
FROM Fact_Orders o
JOIN Dim_Dates d ON o.date_id = d.date_id
WHERE o.status = 'Completed'
GROUP BY d.year
ORDER BY d.year;


-- Monthly revenue trend (completed orders only)
SELECT
    o.date_id                           AS month,
    COUNT(DISTINCT o.order_id)          AS orders,
    ROUND(SUM(o.total_amount), 2)       AS revenue
FROM Fact_Orders o
WHERE o.status = 'Completed'
GROUP BY o.date_id
ORDER BY o.date_id;


-- Revenue by quarter
SELECT
    d.year,
    d.quarter,
    ROUND(SUM(o.total_amount), 2)       AS revenue,
    COUNT(DISTINCT o.order_id)          AS orders
FROM Fact_Orders o
JOIN Dim_Dates d ON o.date_id = d.date_id
WHERE o.status = 'Completed'
GROUP BY d.year, d.quarter
ORDER BY d.year, d.quarter;


-- ─────────────────────────────────────────
-- 2. PRODUCT PERFORMANCE
-- ─────────────────────────────────────────

-- Revenue and gross profit by product
SELECT
    p.product_name,
    p.category,
    p.brand,
    SUM(oi.quantity)                                            AS units_sold,
    ROUND(SUM(oi.total_price), 2)                              AS revenue,
    ROUND(SUM(oi.total_price - p.cost * oi.quantity), 2)       AS gross_profit,
    ROUND(
        100.0 * SUM(oi.total_price - p.cost * oi.quantity)
        / NULLIF(SUM(oi.total_price), 0), 1
    )                                                           AS margin_pct
FROM Fact_Order_Items oi
JOIN Dim_Products p      ON oi.product_id = p.product_id
JOIN Fact_Orders o       ON oi.order_id   = o.order_id
WHERE o.status = 'Completed'
GROUP BY p.product_id
ORDER BY revenue DESC;


-- Revenue by category
SELECT
    p.category,
    SUM(oi.quantity)                    AS units_sold,
    ROUND(SUM(oi.total_price), 2)       AS revenue,
    ROUND(
        100.0 * SUM(oi.total_price)
        / SUM(SUM(oi.total_price)) OVER (), 1
    )                                   AS revenue_share_pct
FROM Fact_Order_Items oi
JOIN Dim_Products p  ON oi.product_id = p.product_id
JOIN Fact_Orders o   ON oi.order_id   = o.order_id
WHERE o.status = 'Completed'
GROUP BY p.category
ORDER BY revenue DESC;


-- ─────────────────────────────────────────
-- 3. CUSTOMER ANALYTICS
-- ─────────────────────────────────────────

-- Top 20 customers by lifetime value
SELECT
    c.customer_id,
    c.first_name || ' ' || c.last_name  AS customer_name,
    c.customer_segment,
    r.region_name,
    COUNT(DISTINCT o.order_id)          AS total_orders,
    ROUND(SUM(o.total_amount), 2)       AS lifetime_value,
    ROUND(AVG(o.total_amount), 2)       AS avg_order_value
FROM Fact_Orders o
JOIN Dim_Customers c ON o.customer_id = c.customer_id
JOIN Dim_Regions r   ON c.region_id   = r.region_id
WHERE o.status = 'Completed'
GROUP BY c.customer_id
ORDER BY lifetime_value DESC
LIMIT 20;


-- RFM segmentation (Recency / Frequency / Monetary)
WITH rfm AS (
    SELECT
        o.customer_id,
        MAX(o.date_id)                      AS last_order_month,
        COUNT(DISTINCT o.order_id)          AS frequency,
        ROUND(SUM(o.total_amount), 2)       AS monetary
    FROM Fact_Orders o
    WHERE o.status = 'Completed'
    GROUP BY o.customer_id
),
rfm_scored AS (
    SELECT *,
        NTILE(5) OVER (ORDER BY last_order_month)  AS r_score,
        NTILE(5) OVER (ORDER BY frequency)         AS f_score,
        NTILE(5) OVER (ORDER BY monetary)          AS m_score
    FROM rfm
)
SELECT
    customer_id,
    last_order_month,
    frequency,
    monetary,
    r_score,
    f_score,
    m_score,
    r_score + f_score + m_score             AS rfm_total,
    CASE
        WHEN r_score >= 4 AND f_score >= 4  THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 3  THEN 'Loyal'
        WHEN r_score >= 4 AND f_score <= 2  THEN 'New Customers'
        WHEN r_score <= 2 AND f_score >= 3  THEN 'At Risk'
        WHEN r_score <= 2 AND f_score <= 2  THEN 'Lost'
        ELSE 'Potential'
    END                                     AS rfm_segment
FROM rfm_scored
ORDER BY rfm_total DESC;


-- Customer count and revenue share by segment
SELECT
    c.customer_segment,
    COUNT(DISTINCT c.customer_id)       AS customers,
    COUNT(DISTINCT o.order_id)          AS orders,
    ROUND(SUM(o.total_amount), 2)       AS revenue,
    ROUND(AVG(o.total_amount), 2)       AS avg_order_value,
    ROUND(
        100.0 * SUM(o.total_amount)
        / SUM(SUM(o.total_amount)) OVER (), 1
    )                                   AS revenue_share_pct
FROM Dim_Customers c
JOIN Fact_Orders o ON c.customer_id = o.customer_id
WHERE o.status = 'Completed'
GROUP BY c.customer_segment
ORDER BY revenue DESC;


-- New customers acquired per month
SELECT
    strftime('%Y-%m', c.join_date)      AS cohort_month,
    COUNT(*)                            AS new_customers
FROM Dim_Customers c
GROUP BY cohort_month
ORDER BY cohort_month;


-- ─────────────────────────────────────────
-- 4. REGIONAL ANALYSIS
-- ─────────────────────────────────────────

-- Revenue and AOV by region
SELECT
    r.region_name,
    COUNT(DISTINCT o.order_id)          AS orders,
    COUNT(DISTINCT c.customer_id)       AS customers,
    ROUND(SUM(o.total_amount), 2)       AS revenue,
    ROUND(AVG(o.total_amount), 2)       AS avg_order_value
FROM Fact_Orders o
JOIN Dim_Regions r   ON o.region_id   = r.region_id
JOIN Dim_Customers c ON o.customer_id = c.customer_id
WHERE o.status = 'Completed'
GROUP BY r.region_id
ORDER BY revenue DESC;


-- ─────────────────────────────────────────
-- 5. ORDER QUALITY & RETURNS
-- ─────────────────────────────────────────

-- Return and cancellation rates overall
SELECT
    status,
    COUNT(*)                            AS order_count,
    ROUND(
        100.0 * COUNT(*)
        / SUM(COUNT(*)) OVER (), 1
    )                                   AS pct_of_total
FROM Fact_Orders
GROUP BY status
ORDER BY order_count DESC;


-- Return rate by customer segment
SELECT
    c.customer_segment,
    COUNT(DISTINCT o.order_id)          AS total_orders,
    SUM(CASE WHEN o.status = 'Returned'   THEN 1 ELSE 0 END)   AS returned,
    SUM(CASE WHEN o.status = 'Cancelled'  THEN 1 ELSE 0 END)   AS cancelled,
    ROUND(
        100.0 * SUM(CASE WHEN o.status = 'Returned' THEN 1 ELSE 0 END)
        / COUNT(*), 1
    )                                   AS return_rate_pct
FROM Fact_Orders o
JOIN Dim_Customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_segment
ORDER BY return_rate_pct DESC;


-- ─────────────────────────────────────────
-- 6. DEMOGRAPHIC BREAKDOWN
-- ─────────────────────────────────────────

-- Revenue by gender
SELECT
    c.gender,
    COUNT(DISTINCT c.customer_id)       AS customers,
    ROUND(SUM(o.total_amount), 2)       AS revenue,
    ROUND(AVG(o.total_amount), 2)       AS avg_order_value
FROM Fact_Orders o
JOIN Dim_Customers c ON o.customer_id = c.customer_id
WHERE o.status = 'Completed'
GROUP BY c.gender
ORDER BY revenue DESC;


-- Revenue by age band
SELECT
    CASE
        WHEN c.age BETWEEN 18 AND 24 THEN '18-24'
        WHEN c.age BETWEEN 25 AND 34 THEN '25-34'
        WHEN c.age BETWEEN 35 AND 44 THEN '35-44'
        WHEN c.age BETWEEN 45 AND 54 THEN '45-54'
        ELSE '55+'
    END                                 AS age_band,
    COUNT(DISTINCT c.customer_id)       AS customers,
    ROUND(SUM(o.total_amount), 2)       AS revenue,
    ROUND(AVG(o.total_amount), 2)       AS avg_order_value
FROM Fact_Orders o
JOIN Dim_Customers c ON o.customer_id = c.customer_id
WHERE o.status = 'Completed'
GROUP BY age_band
ORDER BY age_band;