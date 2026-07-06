-- Enterprise Retail Analytics - Logical Views (MySQL)

USE nestasia_dwh;

-- 1. Daily Executive Summary
CREATE OR REPLACE VIEW vw_executive_daily AS
SELECT 
    d.full_date,
    SUM(s.gross_sales) AS daily_gross_revenue,
    SUM(s.net_sales) AS daily_net_revenue,
    SUM(s.profit) AS daily_profit,
    COUNT(DISTINCT s.order_id) AS total_orders,
    SUM(s.quantity) AS units_sold
FROM Fact_Sales s
JOIN Dim_Date d ON s.date_sk = d.date_sk
GROUP BY d.full_date;

-- 2. Customer Profile Value
CREATE OR REPLACE VIEW vw_customer_profile_value AS
SELECT 
    c.customer_id,
    c.age_group,
    c.loyalty_tier,
    c.customer_segment,
    COUNT(DISTINCT s.order_id) AS total_purchases,
    SUM(s.net_sales) AS actual_ltv,
    c.estimated_clv AS predicted_clv
FROM Fact_Sales s
JOIN Dim_Customer c ON s.customer_sk = c.customer_sk
GROUP BY c.customer_id, c.age_group, c.loyalty_tier, c.customer_segment, c.estimated_clv;

-- 3. Product Performance Analysis
CREATE OR REPLACE VIEW vw_product_performance AS
SELECT 
    p.sku,
    p.brand,
    p.collection,
    SUM(s.quantity) AS total_units_sold,
    SUM(s.net_sales) AS total_revenue,
    SUM(s.profit) AS total_profit,
    AVG(s.margin) AS avg_margin
FROM Fact_Sales s
JOIN Dim_Product p ON s.product_sk = p.product_sk
GROUP BY p.sku, p.brand, p.collection;

-- 4. Inventory Risk
CREATE OR REPLACE VIEW vw_inventory_risk AS
SELECT 
    w.warehouse_name,
    p.sku,
    i.closing_stock,
    i.inventory_value,
    CASE 
        WHEN i.closing_stock = 0 THEN 'Out of Stock'
        WHEN i.closing_stock < 50 THEN 'Low Stock'
        ELSE 'Healthy'
    END AS stock_status
FROM Fact_Inventory i
JOIN Dim_Product p ON i.product_sk = p.product_sk
JOIN Dim_Warehouse w ON i.warehouse_sk = w.warehouse_sk
WHERE i.date_sk = (SELECT MAX(date_sk) FROM Fact_Inventory);
