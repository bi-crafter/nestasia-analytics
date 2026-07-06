-- Enterprise Retail Analytics - Data Warehouse Schema (MySQL)

CREATE DATABASE IF NOT EXISTS nestasia_dwh;
USE nestasia_dwh;

-- =========================================
-- DIMENSION TABLES
-- =========================================

CREATE TABLE Dim_Date (
    date_sk INT PRIMARY KEY,
    full_date DATE NOT NULL,
    year INT,
    month INT,
    day INT,
    quarter INT,
    day_of_week INT,
    is_weekend BOOLEAN
);

CREATE TABLE Dim_Geography (
    geography_sk INT PRIMARY KEY,
    zip_code VARCHAR(50),
    city VARCHAR(100),
    state VARCHAR(50)
);

CREATE TABLE Dim_Category (
    category_sk INT PRIMARY KEY,
    category_name VARCHAR(100),
    category_name_english VARCHAR(100)
);

CREATE TABLE Dim_Product (
    product_sk INT PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL UNIQUE,
    sku VARCHAR(50),
    brand VARCHAR(50),
    collection VARCHAR(100),
    material VARCHAR(50),
    color VARCHAR(50),
    size VARCHAR(50),
    supplier VARCHAR(100),
    cost_price DECIMAL(10,2),
    mrp DECIMAL(10,2),
    launch_date DATE,
    product_status VARCHAR(50)
);

CREATE TABLE Dim_Customer (
    customer_sk INT PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL UNIQUE,
    gender VARCHAR(20),
    age INT,
    age_group VARCHAR(20),
    income_segment VARCHAR(50),
    city VARCHAR(100),
    state VARCHAR(50),
    country VARCHAR(50),
    loyalty_tier VARCHAR(50),
    signup_date DATE,
    preferred_channel VARCHAR(50),
    customer_segment VARCHAR(50),
    estimated_clv DECIMAL(15,2)
);

CREATE TABLE Dim_Seller (
    seller_sk INT PRIMARY KEY,
    seller_id VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE Dim_Warehouse (
    warehouse_sk INT PRIMARY KEY,
    warehouse_id VARCHAR(50) NOT NULL UNIQUE,
    warehouse_name VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(50),
    country VARCHAR(50),
    capacity INT,
    manager VARCHAR(100),
    warehouse_type VARCHAR(50),
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8)
);

CREATE TABLE Dim_Campaign (
    campaign_sk INT PRIMARY KEY,
    campaign_id VARCHAR(50) NOT NULL UNIQUE,
    campaign_name VARCHAR(255),
    channel VARCHAR(50),
    campaign_type VARCHAR(50),
    start_date DATE,
    end_date DATE
);

CREATE TABLE Dim_Payment (
    payment_sk INT PRIMARY KEY,
    payment_type VARCHAR(50)
);

CREATE TABLE Dim_Shipping (
    shipping_sk INT PRIMARY KEY,
    carrier VARCHAR(100),
    shipping_method VARCHAR(50)
);

-- =========================================
-- FACT TABLES
-- =========================================

CREATE TABLE Fact_Sales (
    sales_sk INT PRIMARY KEY,
    order_id VARCHAR(50),
    order_item_id INT,
    date_sk INT,
    customer_sk INT,
    seller_sk INT,
    product_sk INT,
    payment_sk INT,
    geography_sk INT,
    quantity INT,
    unit_price DECIMAL(10,2),
    discount DECIMAL(10,2),
    freight_cost DECIMAL(10,2),
    cost_price DECIMAL(10,2),
    gross_sales DECIMAL(15,2),
    net_sales DECIMAL(15,2),
    profit DECIMAL(15,2),
    margin DECIMAL(10,4),
    delivery_days INT,
    is_delivered BOOLEAN
);

CREATE TABLE Fact_Inventory (
    inventory_sk INT PRIMARY KEY,
    date_sk INT,
    warehouse_sk INT,
    product_sk INT,
    opening_stock INT,
    received_stock INT,
    sold_stock INT,
    damaged_stock INT,
    closing_stock INT,
    inventory_value DECIMAL(15,2)
);

CREATE TABLE Fact_Marketing (
    marketing_sk INT PRIMARY KEY,
    campaign_sk INT,
    date_sk INT,
    spend DECIMAL(15,2),
    impressions INT,
    clicks INT,
    ctr DECIMAL(10,4),
    conversions INT,
    revenue DECIMAL(15,2),
    roas DECIMAL(10,4),
    cpa DECIMAL(10,2)
);

CREATE TABLE Fact_Returns (
    return_sk INT PRIMARY KEY,
    date_sk INT,
    customer_sk INT,
    product_sk INT,
    reason VARCHAR(255),
    return_value DECIMAL(15,2),
    refund_amount DECIMAL(15,2),
    days_to_return INT
);

CREATE TABLE Fact_Reviews (
    review_sk INT PRIMARY KEY,
    date_sk INT,
    customer_sk INT,
    product_sk INT,
    review_score DECIMAL(5,2),
    sentiment_score DECIMAL(5,2),
    review_length INT
);

CREATE TABLE Fact_Payments (
    payment_sk INT PRIMARY KEY,
    date_sk INT,
    customer_sk INT,
    payment_method VARCHAR(50),
    installments INT,
    payment_value DECIMAL(15,2)
);

CREATE TABLE Fact_Shipping (
    shipping_sk INT PRIMARY KEY,
    date_sk INT,
    seller_sk INT,
    customer_sk INT,
    carrier VARCHAR(100),
    shipping_method VARCHAR(50),
    shipping_cost DECIMAL(10,2),
    estimated_days INT,
    actual_days INT,
    late_delivery BOOLEAN
);
