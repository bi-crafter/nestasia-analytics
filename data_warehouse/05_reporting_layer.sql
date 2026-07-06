-- Enterprise Retail Analytics - Reporting Layer MVs (MySQL)

USE nestasia_dwh;

-- =========================================
-- MATERIALIZED VIEWS (Summary Tables)
-- =========================================

DROP TABLE IF EXISTS mv_sales_daily;
CREATE TABLE mv_sales_daily (
    date_sk INT PRIMARY KEY,
    full_date DATE,
    total_orders INT,
    total_revenue DECIMAL(15,2),
    total_profit DECIMAL(15,2)
);

DROP TABLE IF EXISTS mv_sales_monthly;
CREATE TABLE mv_sales_monthly (
    year INT,
    month INT,
    total_orders INT,
    total_revenue DECIMAL(15,2),
    total_profit DECIMAL(15,2),
    PRIMARY KEY (year, month)
);

DROP TABLE IF EXISTS mv_sales_yearly;
CREATE TABLE mv_sales_yearly (
    year INT PRIMARY KEY,
    total_orders INT,
    total_revenue DECIMAL(15,2)
);

DROP TABLE IF EXISTS mv_top_products;
CREATE TABLE mv_top_products (
    product_sk INT PRIMARY KEY,
    sku VARCHAR(50),
    collection VARCHAR(100),
    units_sold INT,
    total_revenue DECIMAL(15,2)
);

DROP TABLE IF EXISTS mv_customer_ltv;
CREATE TABLE mv_customer_ltv (
    customer_sk INT PRIMARY KEY,
    loyalty_tier VARCHAR(50),
    total_purchases INT,
    lifetime_value DECIMAL(15,2)
);

DROP TABLE IF EXISTS mv_customer_retention;
CREATE TABLE mv_customer_retention (
    year INT,
    month INT,
    new_customers INT,
    returning_customers INT,
    PRIMARY KEY (year, month)
);

DROP TABLE IF EXISTS mv_region_sales;
CREATE TABLE mv_region_sales (
    state VARCHAR(50) PRIMARY KEY,
    total_orders INT,
    total_revenue DECIMAL(15,2)
);

DROP TABLE IF EXISTS mv_inventory_health;
CREATE TABLE mv_inventory_health (
    warehouse_sk INT,
    product_sk INT,
    closing_stock INT,
    stock_status VARCHAR(50),
    PRIMARY KEY (warehouse_sk, product_sk)
);

DROP TABLE IF EXISTS mv_shipping_performance;
CREATE TABLE mv_shipping_performance (
    carrier VARCHAR(100) PRIMARY KEY,
    avg_delivery_days DECIMAL(5,2),
    late_deliveries INT
);

DROP TABLE IF EXISTS mv_marketing_roi;
CREATE TABLE mv_marketing_roi (
    campaign_sk INT PRIMARY KEY,
    spend DECIMAL(15,2),
    revenue DECIMAL(15,2),
    roas DECIMAL(10,2)
);

DROP TABLE IF EXISTS mv_category_sales;
CREATE TABLE mv_category_sales (
    collection VARCHAR(100) PRIMARY KEY,
    total_revenue DECIMAL(15,2)
);

DROP TABLE IF EXISTS mv_return_analysis;
CREATE TABLE mv_return_analysis (
    product_sk INT PRIMARY KEY,
    total_returns INT,
    refund_amount DECIMAL(15,2)
);

DROP TABLE IF EXISTS mv_cohort_analysis;
CREATE TABLE mv_cohort_analysis (
    cohort_year INT,
    cohort_month INT,
    months_since INT,
    retained_customers INT,
    PRIMARY KEY (cohort_year, cohort_month, months_since)
);

-- =========================================
-- REFRESH PROCEDURE
-- =========================================

DELIMITER //

CREATE PROCEDURE sp_refresh_reporting_layer()
BEGIN
    -- Refresh mv_sales_daily
    TRUNCATE TABLE mv_sales_daily;
    INSERT INTO mv_sales_daily
    SELECT s.date_sk, d.full_date, COUNT(DISTINCT s.order_id), SUM(s.net_sales), SUM(s.profit)
    FROM Fact_Sales s JOIN Dim_Date d ON s.date_sk = d.date_sk
    GROUP BY s.date_sk, d.full_date;

    -- Refresh mv_sales_monthly
    TRUNCATE TABLE mv_sales_monthly;
    INSERT INTO mv_sales_monthly
    SELECT d.year, d.month, COUNT(DISTINCT s.order_id), SUM(s.net_sales), SUM(s.profit)
    FROM Fact_Sales s JOIN Dim_Date d ON s.date_sk = d.date_sk
    GROUP BY d.year, d.month;
    
    -- Refresh mv_sales_yearly
    TRUNCATE TABLE mv_sales_yearly;
    INSERT INTO mv_sales_yearly
    SELECT d.year, COUNT(DISTINCT s.order_id), SUM(s.net_sales)
    FROM Fact_Sales s JOIN Dim_Date d ON s.date_sk = d.date_sk
    GROUP BY d.year;

    -- Refresh mv_top_products
    TRUNCATE TABLE mv_top_products;
    INSERT INTO mv_top_products
    SELECT p.product_sk, p.sku, p.collection, SUM(s.quantity), SUM(s.net_sales)
    FROM Fact_Sales s JOIN Dim_Product p ON s.product_sk = p.product_sk
    GROUP BY p.product_sk, p.sku, p.collection;

    -- Refresh mv_customer_ltv
    TRUNCATE TABLE mv_customer_ltv;
    INSERT INTO mv_customer_ltv
    SELECT c.customer_sk, c.loyalty_tier, COUNT(DISTINCT s.order_id), SUM(s.net_sales)
    FROM Fact_Sales s JOIN Dim_Customer c ON s.customer_sk = c.customer_sk
    GROUP BY c.customer_sk, c.loyalty_tier;

    -- Refresh mv_customer_retention
    TRUNCATE TABLE mv_customer_retention;
    INSERT INTO mv_customer_retention
    SELECT d.year, d.month, 
           COUNT(DISTINCT CASE WHEN t.is_new = 1 THEN t.customer_sk END), 
           COUNT(DISTINCT CASE WHEN t.is_new = 0 THEN t.customer_sk END)
    FROM (
        SELECT s.customer_sk, d2.year, d2.month, 
               CASE WHEN MIN(s.date_sk) OVER (PARTITION BY s.customer_sk) = s.date_sk THEN 1 ELSE 0 END AS is_new
        FROM Fact_Sales s JOIN Dim_Date d2 ON s.date_sk = d2.date_sk
    ) t JOIN Dim_Date d ON t.year = d.year AND t.month = d.month
    GROUP BY d.year, d.month;

    -- Refresh mv_region_sales
    TRUNCATE TABLE mv_region_sales;
    INSERT INTO mv_region_sales
    SELECT g.state, COUNT(DISTINCT s.order_id), SUM(s.net_sales)
    FROM Fact_Sales s JOIN Dim_Geography g ON s.geography_sk = g.geography_sk
    GROUP BY g.state;

    -- Refresh mv_inventory_health
    TRUNCATE TABLE mv_inventory_health;
    INSERT INTO mv_inventory_health
    SELECT warehouse_sk, product_sk, closing_stock, 
           CASE WHEN closing_stock = 0 THEN 'Out of Stock' 
                WHEN closing_stock < 10 THEN 'Low Stock' 
                ELSE 'Healthy' END
    FROM Fact_Inventory
    WHERE date_sk = (SELECT MAX(date_sk) FROM Fact_Inventory);

    -- Refresh mv_shipping_performance
    TRUNCATE TABLE mv_shipping_performance;
    INSERT INTO mv_shipping_performance
    SELECT carrier, AVG(actual_days), SUM(CASE WHEN late_delivery = 1 THEN 1 ELSE 0 END)
    FROM Fact_Shipping
    GROUP BY carrier;

    -- Refresh mv_marketing_roi
    TRUNCATE TABLE mv_marketing_roi;
    INSERT INTO mv_marketing_roi
    SELECT campaign_sk, SUM(spend), SUM(revenue), 
           CASE WHEN SUM(spend) > 0 THEN SUM(revenue)/SUM(spend) ELSE 0 END
    FROM Fact_Marketing
    GROUP BY campaign_sk;

    -- Refresh mv_category_sales
    TRUNCATE TABLE mv_category_sales;
    INSERT INTO mv_category_sales
    SELECT p.collection, SUM(s.net_sales)
    FROM Fact_Sales s JOIN Dim_Product p ON s.product_sk = p.product_sk
    GROUP BY p.collection;

    -- Refresh mv_return_analysis
    TRUNCATE TABLE mv_return_analysis;
    INSERT INTO mv_return_analysis
    SELECT product_sk, COUNT(*), SUM(refund_amount)
    FROM Fact_Returns
    GROUP BY product_sk;

    -- Refresh mv_cohort_analysis
    TRUNCATE TABLE mv_cohort_analysis;
    INSERT INTO mv_cohort_analysis
    SELECT c.cohort_year, c.cohort_month, 
           (d.year - c.cohort_year) * 12 + (d.month - c.cohort_month) AS months_since, 
           COUNT(DISTINCT s.customer_sk)
    FROM Fact_Sales s
    JOIN Dim_Date d ON s.date_sk = d.date_sk
    JOIN (
       SELECT customer_sk, MIN(date_sk) AS first_date_sk
       FROM Fact_Sales 
       GROUP BY customer_sk
    ) first_order ON s.customer_sk = first_order.customer_sk
    JOIN Dim_Date d2 ON first_order.first_date_sk = d2.date_sk
    JOIN (SELECT customer_sk, year AS cohort_year, month AS cohort_month FROM Fact_Sales fs JOIN Dim_Date fd ON fs.date_sk = fd.date_sk GROUP BY customer_sk, year, month) c ON s.customer_sk = c.customer_sk
    GROUP BY c.cohort_year, c.cohort_month, months_since;
END //

DELIMITER ;

-- =========================================
-- EVENT SCHEDULER
-- =========================================

CREATE EVENT IF NOT EXISTS ev_refresh_reporting_layer
ON SCHEDULE EVERY 1 DAY STARTS (TIMESTAMP(CURRENT_DATE) + INTERVAL 1 DAY + INTERVAL 3 HOUR)
DO CALL sp_refresh_reporting_layer();
